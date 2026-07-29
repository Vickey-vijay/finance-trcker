"""Transaction classification, merchant naming and payment-rail detection."""
import pytest

import classifier


@pytest.mark.parametrize("narration,expected", [
    ("UPI-SWIGGY-OKAXIS-XXXX1234", "Food & Dining"),
    ("UPI-ZOMATO-OKICICI-XXXX5678", "Food & Dining"),
    ("POS-4521-RELIANCE FRESH", "Groceries"),
    ("UPI-BIGBASKET-OKAXIS-1122", "Groceries"),
    ("NETFLIX SUBSCRIPTION", "Subscriptions"),
    ("NACH-LIC PREMIUM-AUTODEBIT", "Insurance"),
    ("ACH-D- HDB FINANCIAL-CARLOAN EMI", "EMI / Loans"),
    ("SIP ZERODHA COIN MUTUAL FUND", "Investments"),
    ("BBPS TNEB ELECTRICITY BILL", "Utilities"),
    ("UPI-UBER INDIA-OKHDFC-9988", "Transport"),
    ("NEFT-DR-RENT TRANSFER LANDLORD", "Rent"),
    ("UPI-AMAZON-OKAXIS-4471", "Shopping"),
    ("UPI-APOLLO PHARMACY-YBL-3312", "Health"),
    ("BOOKMYSHOW TICKETS", "Entertainment"),
    ("MAKEMYTRIP FLIGHT BOOKING", "Travel"),
])
def test_known_merchants_land_in_the_right_category(narration, expected):
    assert classifier.classify(narration, "debit") == expected


def test_a_upi_payment_to_a_merchant_is_not_filed_as_a_transfer():
    """The payment rail must never outrank the merchant name. A UPI payment to
    Swiggy is food, not an anonymous transfer."""
    for narration in ("UPI-SWIGGY-OKAXIS-XXXX1234",
                      "UPI-BIGBASKET-OKAXIS-1122",
                      "IMPS-NETFLIX-4471",
                      "NEFT-DR-RENT TRANSFER LANDLORD"):
        assert classifier.classify(narration, "debit") != "Transfers"


def test_a_person_to_person_payment_is_a_transfer():
    assert classifier.classify("UPI-RAHUL SHARMA-YBL-8891", "debit") == "Transfers"


def test_salary_credit_is_income():
    assert classifier.classify("SALARY CREDIT ACME TECH PVT LTD", "credit") == "Income"


def test_income_keywords_do_not_capture_a_debit():
    assert classifier.classify("INTEREST ON CAR LOAN EMI", "debit") != "Income"


def test_premium_is_not_read_as_emi():
    """'EMI' appears inside 'PREMIUM'; a substring match would misfile it."""
    assert classifier.classify("NACH-LIC PREMIUM-AUTODEBIT", "debit") == "Insurance"


@pytest.mark.parametrize("narration,expected", [
    ("UPI-SWIGGY-OKAXIS-XXXX1234", "UPI"),
    ("NEFT-DR-RENT TRANSFER LANDLORD", "NEFT"),
    ("NACH-LIC PREMIUM-AUTODEBIT", "NACH"),
    ("POS-4521-RELIANCE FRESH", "POS"),
    ("ATM WDL SBIN0001234", "ATM-CW"),
])
def test_payment_rail_detection(narration, expected):
    assert classifier.detect_method(narration) == expected


@pytest.mark.parametrize("narration,expected", [
    ("UPI-SWIGGY-OKAXIS-XXXX1234", "Swiggy"),
    ("POS-4521-RELIANCE FRESH", "Reliance Fresh"),
    ("NACH-LIC PREMIUM-AUTODEBIT", "LIC"),
    ("NETFLIX SUBSCRIPTION", "Netflix"),
])
def test_merchant_names_are_normalised(narration, expected):
    assert classifier.merchant_name(narration) == expected


@pytest.mark.parametrize("narration", [
    "UPI-OLA CABS-OKSBI-XXXX1234",
    "UPI-UBER INDIA-OKHDFC-9988",
    "POS-4521-RELIANCE FRESH",
])
def test_readable_labels_drop_handles_and_reference_numbers(narration):
    cleaned = classifier.clean_description(narration)
    lowered = cleaned.lower()
    assert "oksbi" not in lowered and "okhdfc" not in lowered
    assert "xxxx" not in lowered
    assert not any(part.isdigit() and len(part) >= 3 for part in cleaned.split())


def test_a_bank_handle_that_is_also_a_merchant_survives():
    """Airtel is a payee as well as a UPI handle, so the word must be kept."""
    assert "airtel" in classifier.clean_description("UPI-AIRTEL PREPAID-YBL-771").lower()


def test_confidence_and_source_are_reported():
    category, confidence, source = classifier.classify_with_confidence(
        "UPI-SWIGGY-OKAXIS-XXXX1234", "debit")
    assert category == "Food & Dining"
    assert confidence == 1.0
    assert source == "rule"


def test_unknown_narration_still_returns_a_valid_category():
    category, confidence, source = classifier.classify_with_confidence("ZZQQ 8891 XY", "debit")
    assert category in classifier.CATEGORIES
    assert 0.0 <= confidence <= 1.0
    assert source in ("rule", "model")


def test_category_list_is_the_agreed_seventeen():
    assert len(classifier.CATEGORIES) == 17
    assert classifier.CATEGORIES[0] == "Income"
    assert classifier.CATEGORIES[-1] == "Others"
