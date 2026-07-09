"""Bank statement parser. Handles CSV and PDF (Indian bank layouts)."""
import io
import re
from datetime import datetime

import pandas as pd

try:
    import pdfplumber
    HAS_PDF = True
except Exception:
    HAS_PDF = False

DATE_FORMATS = [
    "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y",
    "%Y-%m-%d", "%d %b %Y", "%d-%b-%Y", "%d-%b-%y",
    "%m/%d/%Y", "%d.%m.%Y",
]

# Column-name aliases seen across SBI/HDFC/ICICI/Axis exports.
DATE_COLS = ["date", "txn date", "transaction date", "value date", "tran date", "posting date"]
DESC_COLS = ["description", "narration", "particulars", "details", "remarks",
             "transaction details", "transaction remarks", "narration / description"]
DEBIT_COLS = ["debit", "withdrawal", "withdrawal amt", "withdrawal amt.", "dr", "debit amount",
              "withdrawal (dr)", "withdrawals"]
CREDIT_COLS = ["credit", "deposit", "deposit amt", "deposit amt.", "cr", "credit amount",
               "deposit (cr)", "deposits"]
AMOUNT_COLS = ["amount", "transaction amount", "amt"]


def parse_date(value):
    if value is None:
        return None
    s = str(value).strip().split(" ")[0] if isinstance(value, str) else str(value)
    s = s.strip()
    if not s or s.lower() in ("nan", "none"):
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s.split(" ")[0], fmt).date()
        except Exception:
            continue
    try:
        return pd.to_datetime(s, dayfirst=True, errors="coerce").date()
    except Exception:
        return None


def parse_amount(value):
    if value is None:
        return None
    s = str(value).strip()
    if not s or s.lower() in ("nan", "none", "-"):
        return None
    neg = "(" in s and ")" in s
    s = re.sub(r"[^0-9.\-]", "", s.replace(",", ""))
    if s in ("", "-", "."):
        return None
    try:
        amt = float(s)
        return -abs(amt) if neg else amt
    except Exception:
        return None


def _find_col(columns, aliases):
    lower = {c.lower().strip(): c for c in columns}
    for a in aliases:
        if a in lower:
            return lower[a]
    # partial contains match
    for key, original in lower.items():
        for a in aliases:
            if a in key:
                return original
    return None


def _rows_from_dataframe(df):
    df.columns = [str(c).strip() for c in df.columns]
    date_c = _find_col(df.columns, DATE_COLS)
    desc_c = _find_col(df.columns, DESC_COLS)
    debit_c = _find_col(df.columns, DEBIT_COLS)
    credit_c = _find_col(df.columns, CREDIT_COLS)
    amount_c = _find_col(df.columns, AMOUNT_COLS)

    rows = []
    for _, r in df.iterrows():
        desc = str(r.get(desc_c, "")).strip() if desc_c else ""
        if not desc or desc.lower() == "nan":
            continue
        d = parse_date(r.get(date_c)) if date_c else None

        amount, txn_type = None, None
        if debit_c or credit_c:
            deb = parse_amount(r.get(debit_c)) if debit_c else None
            cred = parse_amount(r.get(credit_c)) if credit_c else None
            if cred:
                amount, txn_type = abs(cred), "credit"
            elif deb:
                amount, txn_type = abs(deb), "debit"
        elif amount_c:
            a = parse_amount(r.get(amount_c))
            if a is not None:
                amount = abs(a)
                txn_type = "credit" if a > 0 else "debit"

        if amount is None or amount == 0:
            continue
        rows.append({
            "date": d,
            "raw_description": desc[:300],
            "amount": float(amount),
            "txn_type": txn_type or "debit",
        })
    return rows


def parse_csv(file_bytes):
    df = pd.read_csv(io.BytesIO(file_bytes))
    return _rows_from_dataframe(df)


def parse_pdf(file_bytes):
    if not HAS_PDF:
        raise RuntimeError("pdfplumber not installed; cannot parse PDF.")
    rows = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                if not table or len(table) < 2:
                    continue
                header = [str(c or "").strip() for c in table[0]]
                try:
                    df = pd.DataFrame(table[1:], columns=header)
                except Exception:
                    continue
                rows.extend(_rows_from_dataframe(df))
    return rows


def parse_statement(filename, file_bytes):
    """Dispatch by extension. Returns list of raw transaction dicts."""
    name = (filename or "").lower()
    if name.endswith(".csv"):
        return parse_csv(file_bytes)
    if name.endswith(".pdf"):
        return parse_pdf(file_bytes)
    if name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(file_bytes))
        return _rows_from_dataframe(df)
    raise ValueError("Unsupported file type. Upload a PDF or CSV statement.")
