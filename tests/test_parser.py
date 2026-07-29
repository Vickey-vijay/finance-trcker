"""Statement parsing across the bank layouts the project supports."""
import os
from datetime import date

import pytest

import parser as statement_parser
from conftest import SAMPLE_DIR


def read(name):
    with open(os.path.join(SAMPLE_DIR, name), "rb") as fh:
        return fh.read()


@pytest.mark.parametrize("filename,expected_bank,min_rows", [
    ("sample_statement.csv", None, 25),
    ("hdfc_statement.csv", "HDFC", 35),
    ("icici_statement.csv", "ICICI", 30),
    ("axis_statement.csv", "Axis", 25),
])
def test_each_sample_statement_parses(filename, expected_bank, min_rows):
    result = statement_parser.parse_statement_detailed(filename, read(filename))
    assert result["row_count"] >= min_rows
    assert result["row_count"] == len(result["rows"])
    if expected_bank:
        assert result["bank"] == expected_bank


def test_hdfc_header_is_found_below_the_account_preamble():
    """The HDFC export carries account details above the real header row."""
    result = statement_parser.parse_statement_detailed(
        "hdfc_statement.csv", read("hdfc_statement.csv"))
    assert result["row_count"] >= 35
    assert all(r["amount"] > 0 for r in result["rows"])
    assert all(r["txn_type"] in ("credit", "debit") for r in result["rows"])


def test_axis_direction_inferred_from_running_balance():
    """The Axis layout has one amount column and no debit/credit marker, so the
    direction can only come from the movement in the closing balance."""
    result = statement_parser.parse_statement_detailed(
        "axis_statement.csv", read("axis_statement.csv"))
    kinds = {r["txn_type"] for r in result["rows"]}
    assert kinds == {"credit", "debit"}
    assert any(r["balance"] is not None for r in result["rows"])


def test_opening_balance_rows_are_not_treated_as_transactions():
    result = statement_parser.parse_statement_detailed(
        "axis_statement.csv", read("axis_statement.csv"))
    assert result["skipped"] >= 1
    for row in result["rows"]:
        assert "opening balance" not in row["raw_description"].lower()


def test_pdf_statement_parses_when_the_table_has_no_ruling_lines():
    path = os.path.join(SAMPLE_DIR, "sample_statement.pdf")
    if not os.path.exists(path):
        pytest.skip("sample PDF not generated")
    result = statement_parser.parse_statement_detailed("sample_statement.pdf", read("sample_statement.pdf"))
    assert result["row_count"] >= 25
    assert result["source_format"] == "pdf"


def test_every_row_has_the_agreed_shape():
    rows = statement_parser.parse_statement("sample_statement.csv", read("sample_statement.csv"))
    for row in rows:
        assert set(row) >= {"date", "raw_description", "amount", "txn_type", "balance"}
        assert row["amount"] > 0
        assert row["txn_type"] in ("credit", "debit")
        assert row["date"] is None or isinstance(row["date"], date)


@pytest.mark.parametrize("raw,value,sign", [
    ("1,23,456.00", 123456.00, None),   # Indian lakh grouping
    ("Rs. 4,500", 4500.0, None),        # currency prefix
    ("12,000.00", 12000.0, None),
    ("(2,000.50)", 2000.50, -1),        # parentheses mean a withdrawal
    ("3500.00 Dr", 3500.0, -1),         # explicit debit marker
    ("2750.00 Cr", 2750.0, 1),          # explicit credit marker
    ("", None, None),
    ("-", None, None),
])
def test_indian_amount_formats(raw, value, sign):
    """The parser returns the magnitude and, where the statement states one, the
    direction of the entry."""
    parsed_value, parsed_sign = statement_parser.parse_amount_signed(raw)
    assert parsed_value == value
    assert parsed_sign == sign


@pytest.mark.parametrize("raw,expected", [
    ("01/05/2026", date(2026, 5, 1)),
    ("01-05-2026", date(2026, 5, 1)),
    ("2026-05-01", date(2026, 5, 1)),
    ("01 May 2026", date(2026, 5, 1)),
    ("01-May-2026", date(2026, 5, 1)),
])
def test_mixed_date_formats(raw, expected):
    assert statement_parser.parse_date(raw) == expected


def test_unsupported_file_type_is_reported_in_plain_words():
    with pytest.raises(Exception) as exc:
        statement_parser.parse_statement("statement.docx", b"nonsense")
    assert "upload" in str(exc.value).lower() or "support" in str(exc.value).lower()
