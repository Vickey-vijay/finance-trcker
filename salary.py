"""Indian salary structure and income-tax computation, FY 2025-26.

Pure functions only — no Flask, no database, no I/O — so the tax rules can
be exercised and verified in isolation from the rest of the application.
Money is kept at full precision through every intermediate step and rounded
to two decimals only in the dictionaries returned to the caller.
"""
import calendar
import math
from datetime import date

# --------------------------------------------------------------------------- #
#  Statutory constants, FY 2025-26
# --------------------------------------------------------------------------- #
PF_RATE = 0.12                       # employee and employer PF, each 12% of basic
PF_WAGE_CEILING_MONTHLY = 15000.0    # statutory wage ceiling under the EPF Act
GRATUITY_RATE = 0.0481               # 15/26 days pay per year of service, approximated monthly

STANDARD_DEDUCTION_NEW = 75000.0
STANDARD_DEDUCTION_OLD = 50000.0

NEW_REGIME_REBATE_THRESHOLD = 1200000.0   # Section 87A: nil tax up to this taxable income
NEW_REGIME_REBATE_CAP = 60000.0
OLD_REGIME_REBATE_THRESHOLD = 500000.0
OLD_REGIME_REBATE_CAP = 12500.0

CESS_RATE = 0.04                     # health and education cess on tax after rebate
SECTION_80C_CAP = 150000.0           # aggregate cap; employee PF counts towards it (old regime)

PROFESSIONAL_TAX_ANNUAL = 2400.0
PROFESSIONAL_TAX_STATES = {
    "Tamil Nadu", "Karnataka", "Maharashtra", "West Bengal",
    "Andhra Pradesh", "Telangana", "Gujarat", "Madhya Pradesh",
}

# (lower, upper, rate) — upper of None means "and above".
NEW_REGIME_SLABS = [
    (0.0, 400000.0, 0.00),
    (400000.0, 800000.0, 0.05),
    (800000.0, 1200000.0, 0.10),
    (1200000.0, 1600000.0, 0.15),
    (1600000.0, 2000000.0, 0.20),
    (2000000.0, 2400000.0, 0.25),
    (2400000.0, None, 0.30),
]

OLD_REGIME_SLABS = [
    (0.0, 250000.0, 0.00),
    (250000.0, 500000.0, 0.05),
    (500000.0, 1000000.0, 0.20),
    (1000000.0, None, 0.30),
]


# --------------------------------------------------------------------------- #
#  Slab tax
# --------------------------------------------------------------------------- #
def _slab_tax(taxable_income, slabs):
    """Apply a progressive slab table and return (tax, breakdown rows)."""
    tax = 0.0
    rows = []
    for lower, upper, rate in slabs:
        if taxable_income <= lower:
            break
        band_top = upper if upper is not None else taxable_income
        amount_in_band = min(taxable_income, band_top) - lower
        if amount_in_band <= 0:
            continue
        band_tax = amount_in_band * rate
        tax += band_tax
        range_label = (f"Rs.{lower:,.0f} - Rs.{upper:,.0f}" if upper is not None
                       else f"Above Rs.{lower:,.0f}")
        rows.append({"range": range_label, "rate": f"{rate * 100:.0f}%",
                     "tax": round(band_tax, 2)})
    return tax, rows


def _new_regime_tax_after_rebate(taxable_income):
    """Section 87A rebate with marginal relief for FY 2025-26.

    Taxable income up to Rs.12,00,000 draws a rebate (capped at Rs.60,000)
    that brings tax to nil. Just above that threshold, marginal relief caps
    the tax at the amount of income that lies above Rs.12,00,000, so a
    rupee more of income can never cost more than a rupee of extra tax.
    """
    tax_before_rebate, rows = _slab_tax(taxable_income, NEW_REGIME_SLABS)
    if taxable_income <= NEW_REGIME_REBATE_THRESHOLD:
        rebate = min(tax_before_rebate, NEW_REGIME_REBATE_CAP)
        return max(tax_before_rebate - rebate, 0.0), rows

    income_above_threshold = taxable_income - NEW_REGIME_REBATE_THRESHOLD
    if tax_before_rebate > income_above_threshold:
        return income_above_threshold, rows
    return tax_before_rebate, rows


def _old_regime_tax_after_rebate(taxable_income):
    """Section 87A rebate for the old regime: nil tax up to Rs.5,00,000."""
    tax_before_rebate, rows = _slab_tax(taxable_income, OLD_REGIME_SLABS)
    if taxable_income <= OLD_REGIME_REBATE_THRESHOLD:
        rebate = min(tax_before_rebate, OLD_REGIME_REBATE_CAP)
        return max(tax_before_rebate - rebate, 0.0), rows
    return tax_before_rebate, rows


# --------------------------------------------------------------------------- #
#  Take-home computation
# --------------------------------------------------------------------------- #
def compute_take_home(ctc_annual, basic_pct=0.40, hra_pct=0.50, metro=False,
                      rent_paid_monthly=0.0, regime="new", other_allowances=0.0,
                      pf_opt_in=True, state="Tamil Nadu"):
    ctc_annual = float(ctc_annual)
    other_allowances = float(other_allowances)
    basic = ctc_annual * basic_pct
    hra = basic * hra_pct

    # Employee and employer PF are 12% of basic; opting out of voluntary PF
    # limits the contribution base to the statutory wage ceiling of
    # Rs.15,000 a month rather than the actual basic pay.
    basic_monthly = basic / 12.0
    pf_wage_monthly = basic_monthly if pf_opt_in else min(basic_monthly, PF_WAGE_CEILING_MONTHLY)
    pf_employee = pf_wage_monthly * PF_RATE * 12.0
    pf_employer = pf_wage_monthly * PF_RATE * 12.0

    gratuity = basic * GRATUITY_RATE

    # CTC bundles employer PF and gratuity, which are not paid out monthly;
    # the remainder is the cash gross split into basic, HRA, other
    # allowances and a balancing special allowance.
    cash_gross = ctc_annual - pf_employer - gratuity
    special_allowance = cash_gross - basic - hra - other_allowances
    gross_annual = basic + hra + special_allowance + other_allowances

    if regime == "old":
        rent_annual = rent_paid_monthly * 12.0
        metro_pct = 0.50 if metro else 0.40
        hra_exemption = min(hra, max(rent_annual - 0.10 * basic, 0.0), metro_pct * basic)
        standard_deduction = STANDARD_DEDUCTION_OLD
        # Employee PF is a Section 80C investment, subject to the combined
        # Rs.1,50,000 cap on Chapter VI-A deductions.
        chapter_via = min(pf_employee, SECTION_80C_CAP)
    else:
        hra_exemption = 0.0
        standard_deduction = STANDARD_DEDUCTION_NEW
        chapter_via = 0.0

    taxable_income = max(gross_annual - hra_exemption - standard_deduction - chapter_via, 0.0)

    if regime == "old":
        income_tax, slab_rows = _old_regime_tax_after_rebate(taxable_income)
    else:
        income_tax, slab_rows = _new_regime_tax_after_rebate(taxable_income)

    cess = income_tax * CESS_RATE
    total_tax = income_tax + cess

    professional_tax = PROFESSIONAL_TAX_ANNUAL if state in PROFESSIONAL_TAX_STATES else 0.0

    net_annual = gross_annual - pf_employee - total_tax - professional_tax
    net_monthly = net_annual / 12.0

    return {
        "ctc_annual": round(ctc_annual, 2),
        "basic": round(basic, 2),
        "hra": round(hra, 2),
        "special_allowance": round(special_allowance, 2),
        "other_allowances": round(other_allowances, 2),
        "gross_annual": round(gross_annual, 2),
        "pf_employee": round(pf_employee, 2),
        "pf_employer": round(pf_employer, 2),
        "gratuity": round(gratuity, 2),
        "hra_exemption": round(hra_exemption, 2),
        "standard_deduction": round(standard_deduction, 2),
        "chapter_via": round(chapter_via, 2),
        "taxable_income": round(taxable_income, 2),
        "income_tax": round(income_tax, 2),
        "cess": round(cess, 2),
        "total_tax": round(total_tax, 2),
        "professional_tax": round(professional_tax, 2),
        "net_annual": round(net_annual, 2),
        "net_monthly": round(net_monthly, 2),
        "regime": regime,
        "slab_rows": slab_rows,
        "monthly": {
            "basic": round(basic / 12.0, 2),
            "hra": round(hra / 12.0, 2),
            "special_allowance": round(special_allowance / 12.0, 2),
            "gross": round(gross_annual / 12.0, 2),
            "pf_employee": round(pf_employee / 12.0, 2),
            "tds": round(total_tax / 12.0, 2),
            "professional_tax": round(professional_tax / 12.0, 2),
            "net": round(net_monthly, 2),
        },
    }


def compare_regimes(**kwargs):
    """Run compute_take_home under both regimes and report the better one."""
    old_kwargs = dict(kwargs)
    old_kwargs["regime"] = "old"
    new_kwargs = dict(kwargs)
    new_kwargs["regime"] = "new"

    old_result = compute_take_home(**old_kwargs)
    new_result = compute_take_home(**new_kwargs)
    better = "new" if new_result["net_annual"] >= old_result["net_annual"] else "old"
    saving = abs(new_result["net_annual"] - old_result["net_annual"])
    return {"old": old_result, "new": new_result, "better": better, "saving": round(saving, 2)}


# --------------------------------------------------------------------------- #
#  Goals and salary variance
# --------------------------------------------------------------------------- #
def _add_months(start, months):
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _months_between(start, end):
    return ((end.year - start.year) * 12 + (end.month - start.month)
             - (1 if end.day < start.day else 0))


def goal_projection(target_amount, target_date, saved_amount, monthly_surplus, today=None):
    today = today or date.today()
    target_amount = float(target_amount)
    saved_amount = float(saved_amount)
    monthly_surplus = float(monthly_surplus)
    remaining = max(target_amount - saved_amount, 0.0)
    pct_complete = min((saved_amount / target_amount * 100.0) if target_amount else 0.0, 100.0)

    if remaining <= 0:
        return {"months_left": max(_months_between(today, target_date), 0),
                "required_monthly": 0.0, "on_track": True, "shortfall_monthly": 0.0,
                "projected_completion": today, "pct_complete": round(pct_complete, 2)}

    raw_months_left = _months_between(today, target_date)
    months_left = max(raw_months_left, 0)

    if monthly_surplus > 0:
        months_to_finish = math.ceil(remaining / monthly_surplus)
        projected_completion = _add_months(today, months_to_finish)
    else:
        projected_completion = None

    if months_left <= 0:
        # Target date has already arrived without the goal being met.
        required_monthly = remaining
        on_track = False
    else:
        required_monthly = remaining / months_left
        on_track = monthly_surplus >= required_monthly

    shortfall_monthly = max(required_monthly - monthly_surplus, 0.0)

    return {
        "months_left": months_left,
        "required_monthly": round(required_monthly, 2),
        "on_track": on_track,
        "shortfall_monthly": round(shortfall_monthly, 2),
        "projected_completion": projected_completion,
        "pct_complete": round(pct_complete, 2),
    }


def salary_vs_actual(profile_net_monthly, actual_income_monthly):
    profile_net_monthly = float(profile_net_monthly)
    actual_income_monthly = float(actual_income_monthly)
    variance = actual_income_monthly - profile_net_monthly
    variance_pct = (variance / profile_net_monthly * 100.0) if profile_net_monthly else 0.0

    if profile_net_monthly == 0:
        note = "No salary profile configured to compare against."
    elif abs(variance_pct) <= 5:
        note = "Actual income closely matches the computed salary profile."
    elif variance > 0:
        note = (f"Actual income is Rs.{variance:,.2f} higher than the salary profile, "
               f"{variance_pct:.1f}% above expected.")
    else:
        note = (f"Actual income is Rs.{abs(variance):,.2f} lower than the salary profile, "
               f"{abs(variance_pct):.1f}% below expected.")

    return {
        "expected": round(profile_net_monthly, 2),
        "actual": round(actual_income_monthly, 2),
        "variance": round(variance, 2),
        "variance_pct": round(variance_pct, 2),
        "note": note,
    }
