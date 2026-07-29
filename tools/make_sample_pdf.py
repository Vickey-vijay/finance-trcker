"""Renders sample_data/sample_statement.pdf from sample_statement.csv.

The page is drawn as plain text lines with no ruling lines, the way many
Indian banks actually export a PDF statement, so the sample exercises the
parser's line-by-line text fallback rather than its table extraction path.
"""
import csv
import os
import sys

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
except ImportError:
    print("reportlab is not installed; skipping PDF sample generation. "
          "Install it with: pip install reportlab")
    sys.exit(0)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_PATH = os.path.join(BASE_DIR, "sample_data", "sample_statement.csv")
PDF_PATH = os.path.join(BASE_DIR, "sample_data", "sample_statement.pdf")

OPENING_BALANCE = 50000.00


def _load_rows():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    rows = _load_rows()
    balance = OPENING_BALANCE

    c = canvas.Canvas(PDF_PATH, pagesize=A4)
    width, height = A4
    top = height - 60

    def draw_letterhead(y):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "SAMPLE BANK - Statement of Account")
        y -= 18
        c.setFont("Helvetica", 9)
        c.drawString(50, y, "Account Holder: RAVI KUMAR SHARMA   Account No: 50100987654321")
        y -= 14
        c.drawString(50, y, "Statement Period: 01/05/2026 to 31/05/2026")
        y -= 24
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, y, "Date         Description                                        Amount        Balance")
        y -= 14
        c.setFont("Helvetica", 9)
        return y

    y = draw_letterhead(top)
    c.drawString(50, y, f"01/05/2026  OPENING BALANCE  {balance:.2f}")
    y -= 14

    for row in rows:
        desc = row["Narration"]
        debit = (row.get("Debit") or "").strip()
        credit = (row.get("Credit") or "").strip()
        if credit:
            amt = float(credit)
            balance += amt
            amt_text = f"{amt:.2f} Cr"
        else:
            amt = float(debit)
            balance -= amt
            amt_text = f"{amt:.2f} Dr"

        line = f"{row['Date']}  {desc}  {amt_text}  {balance:.2f}"
        if y < 60:
            c.showPage()
            y = draw_letterhead(top)
        c.drawString(50, y, line)
        y -= 14

    c.save()
    print(f"Wrote {PDF_PATH}")


if __name__ == "__main__":
    main()
