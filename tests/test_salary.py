"""Indian salary structure and income tax for FY 2025-26."""
from datetime import date, timedelta

import pytest

import salary


def test_ctc_reconciles_with_its_components():
    """Gross is the CTC less the employer's own contributions, and take-home is
    gross less the employee's deductions."""
    r = salary.compute_take_home(1800000, regime="new")
    assert r["gross_annual"] == pytest.approx(
        r["ctc_annual"] - r["pf_employer"] - r["gratuity"], rel=1e-6)
    assert r["gross_annual"] == pytest.approx(
        r["basic"] + r["hra"] + r["special_allowance"] + r["other_allowances"], rel=1e-6)
    assert r["net_annual"] == pytest.approx(
        r["gross_annual"] - r["pf_employee"] - r["total_tax"] - r["professional_tax"], rel=1e-6)
    assert r["net_monthly"] == pytest.approx(r["net_annual"] / 12, rel=1e-6)


def test_statutory_percentages():
    r = salary.compute_take_home(1800000, basic_pct=0.40, hra_pct=0.50, regime="new")
    assert r["basic"] == pytest.approx(720000.0)
    assert r["hra"] == pytest.approx(360000.0)
    assert r["pf_employee"] == pytest.approx(0.12 * r["basic"])
    assert r["pf_employer"] == pytest.approx(0.12 * r["basic"])
    assert r["gratuity"] == pytest.approx(0.0481 * r["basic"], rel=1e-4)


def test_cess_is_four_percent_of_tax():
    r = salary.compute_take_home(1800000, regime="new")
    assert r["cess"] == pytest.approx(0.04 * r["income_tax"], rel=1e-6)
    assert r["total_tax"] == pytest.approx(r["income_tax"] + r["cess"], rel=1e-6)


def test_standard_deduction_differs_by_regime():
    assert salary.compute_take_home(1800000, regime="new")["standard_deduction"] == 75000
    assert salary.compute_take_home(1800000, regime="old")["standard_deduction"] == 50000


def test_no_tax_at_the_rebate_threshold_under_the_new_regime():
    r = salary.compute_take_home(1200000, regime="new")
    assert r["taxable_income"] <= 1200000
    assert r["total_tax"] == 0


def test_marginal_relief_holds_just_above_the_rebate_threshold():
    """In the relief band the tax must never exceed the income above Rs.12 lakh,
    otherwise earning one more rupee would cost more than a rupee."""
    for ctc in range(1330000, 1460000, 10000):
        r = salary.compute_take_home(ctc, regime="new")
        excess = r["taxable_income"] - 1200000
        if 0 < excess <= 100000:
            assert r["income_tax"] <= excess + 0.01, (
                f"CTC {ctc}: tax {r['income_tax']} exceeds excess {excess}")


def test_tax_rises_monotonically_with_pay():
    previous = -1.0
    for ctc in (600000, 900000, 1200000, 1500000, 1800000, 2500000, 5000000):
        tax = salary.compute_take_home(ctc, regime="new")["total_tax"]
        assert tax >= previous
        previous = tax


def test_hra_exemption_only_applies_under_the_old_regime():
    kwargs = dict(ctc_annual=1800000, metro=True, rent_paid_monthly=30000)
    assert salary.compute_take_home(regime="new", **kwargs)["hra_exemption"] == 0
    assert salary.compute_take_home(regime="old", **kwargs)["hra_exemption"] > 0


def test_hra_exemption_is_the_smallest_of_the_three_limbs():
    r = salary.compute_take_home(1800000, regime="old", metro=True, rent_paid_monthly=30000)
    actual_hra = r["hra"]
    rent_over_ten_percent = 30000 * 12 - 0.10 * r["basic"]
    metro_share = 0.50 * r["basic"]
    assert r["hra_exemption"] == pytest.approx(
        min(actual_hra, rent_over_ten_percent, metro_share), rel=1e-6)


def test_no_rent_means_no_hra_exemption():
    r = salary.compute_take_home(1800000, regime="old", rent_paid_monthly=0)
    assert r["hra_exemption"] == 0


def test_provident_fund_ceiling_when_the_employee_opts_out():
    opted_in = salary.compute_take_home(1800000, pf_opt_in=True)["pf_employee"]
    opted_out = salary.compute_take_home(1800000, pf_opt_in=False)["pf_employee"]
    assert opted_out < opted_in
    assert opted_out == pytest.approx(0.12 * 15000 * 12, rel=1e-6)


@pytest.mark.parametrize("state,expected", [
    ("Tamil Nadu", 2400.0), ("Karnataka", 2400.0), ("Delhi", 0.0), ("Kerala", 0.0),
])
def test_professional_tax_by_state(state, expected):
    assert salary.compute_take_home(1800000, state=state)["professional_tax"] == expected


def test_slab_rows_sum_to_the_computed_tax():
    r = salary.compute_take_home(2500000, regime="new")
    assert sum(row["tax"] for row in r["slab_rows"]) == pytest.approx(r["income_tax"], rel=1e-6)


def test_regime_comparison_names_the_cheaper_option():
    c = salary.compare_regimes(ctc_annual=1800000)
    assert c["better"] in ("old", "new")
    assert c["saving"] >= 0
    cheaper = c[c["better"]]["net_annual"]
    other = c["old" if c["better"] == "new" else "new"]["net_annual"]
    assert cheaper >= other


def test_goal_on_track_and_behind_schedule():
    target = date.today() + timedelta(days=365)
    ahead = salary.goal_projection(120000, target, 20000, 20000)
    behind = salary.goal_projection(120000, target, 0, 1000)
    assert ahead["on_track"] is True
    assert behind["on_track"] is False
    assert behind["shortfall_monthly"] > 0
    assert 0 <= ahead["pct_complete"] <= 100


def test_goal_already_met():
    r = salary.goal_projection(50000, date.today() + timedelta(days=90), 60000, 5000)
    assert r["pct_complete"] >= 100
    assert r["on_track"] is True
