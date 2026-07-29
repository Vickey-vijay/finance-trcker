"""Bank statement parser for Indian savings-account exports (CSV, XLSX, PDF).

Real net-banking exports rarely start with a clean header row: account holder
name, account number and the statement period sit above the actual column
header, column names vary bank to bank, and PDF statements are often drawn
without ruling lines so no table can be lifted directly. This module scans
for the header row instead of assuming row zero, keeps a per-field alias
table so a new bank is one dictionary entry, and falls back to line-by-line
text parsing when a PDF page yields no usable table.
"""
import csv
import io
import re
from datetime import datetime

import pandas as pd

try:
    import pdfplumber
    HAS_PDF = True
except Exception:
    HAS_PDF = False

# --- Date parsing -------------------------------------------------------- #

DATE_FORMATS = [
    "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y",
    "%Y-%m-%d", "%Y/%m/%d",
    "%d %b %Y", "%d-%b-%Y", "%d-%b-%y", "%d %B %Y", "%d-%B-%Y",
    "%b %d, %Y", "%B %d, %Y", "%m/%d/%Y", "%d.%m.%Y", "%Y.%m.%d",
]


def parse_date(value):
    """Parse a date cell into a date object, or None when it cannot be read.

    Only a trailing time-of-day component is trimmed, not the whole string
    after the first space, so formats such as "01 Jan 2026" are not cut
    down to just "01" before a strptime pattern gets a chance to match.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    s = str(value).strip()
    if not s or s.lower() in ("nan", "none", "nat", "-"):
        return None
    s = re.sub(r"\s+\d{1,2}:\d{2}(:\d{2})?\s*(am|pm)?\s*$", "", s, flags=re.IGNORECASE).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    try:
        parsed = pd.to_datetime(s, dayfirst=True, errors="coerce")
        if pd.isna(parsed):
            return None
        return parsed.date()
    except Exception:
        return None


# --- Amount parsing -------------------------------------------------------- #
# Indian statements mix currency symbols, lakh-style grouping, trailing
# Dr/Cr markers and parenthesised negatives. parse_amount_signed folds all
# of these into one absolute value plus an optional direction flag so the
# same routine can be reused for debit/credit cells, single amount columns
# and running-balance columns.

_CURRENCY_RE = re.compile(r"(rs\.?|inr|₹)", re.IGNORECASE)
_TRAILING_DRCR_RE = re.compile(r"(?i)\b(dr|cr)\b\.?\s*$")
_LEADING_DRCR_RE = re.compile(r"(?i)^(dr|cr)\b\.?\s*")
_BLANK_VALUES = {"", "-", "--", "na", "n/a", "nan", "none", "nil"}


def parse_amount_signed(value):
    """Return (absolute_amount, sign) for a rupee amount cell.

    sign is -1 for a debit marker (parentheses, a leading minus, a unicode
    minus or a trailing/leading "Dr"), +1 for an explicit credit marker
    ("Cr"), or None when the text carries no direction of its own and the
    caller must decide some other way (Dr/Cr type column, balance delta).
    """
    if value is None:
        return None, None
    s = str(value).strip()
    if not s:
        return None, None
    s = s.replace("\xa0", " ").replace("−", "-").strip()
    if s.lower() in _BLANK_VALUES:
        return None, None
    s = _CURRENCY_RE.sub("", s).strip()

    sign = None
    if s.startswith("(") and s.endswith(")") and len(s) > 1:
        sign = -1
        s = s[1:-1].strip()

    m = _TRAILING_DRCR_RE.search(s)
    if m:
        sign = -1 if m.group(1).lower() == "dr" else 1
        s = s[:m.start()].strip()
    elif sign is None:
        m = _LEADING_DRCR_RE.match(s)
        if m:
            sign = -1 if m.group(1).lower() == "dr" else 1
            s = s[m.end():].strip()

    if s.startswith("-"):
        if sign is None:
            sign = -1
        s = s[1:].strip()
    elif s.startswith("+"):
        s = s[1:].strip()

    s = re.sub(r"/-\s*$", "", s)          # trailing "500/-" style
    s = s.replace(",", "").replace(" ", "")
    if s.lower() in _BLANK_VALUES or s in ("", "."):
        return None, None
    try:
        amt = float(s)
    except ValueError:
        return None, None
    return amt, sign


def _signed_balance(value):
    """Balance cells use Dr/Cr to mean overdrawn/normal, not the amount's
    own polarity, so a Cr (or unmarked) balance stays positive and only an
    explicit Dr balance is negative."""
    amt, sign = parse_amount_signed(value)
    if amt is None:
        return None
    return -amt if sign == -1 else amt


# --- Column alias tables --------------------------------------------------- #
# Aliases are stored without periods; headers are normalised the same way
# before comparison. Aliases shorter than four characters ("dr", "cr",
# "amt", "bal") are only accepted as a whole token of the header, never as
# a substring, so a column such as "Address" cannot be picked up by "dr".

FIELD_ALIASES = {
    "date": [
        "date", "txn date", "transaction date", "tran date", "post date",
        "posting date", "transaction dt", "txn dt",
    ],
    "value_date": ["value date", "value dt", "valuedate"],
    "ref": [
        "chq/ref no", "cheque number", "cheque no", "chq no", "ref no",
        "reference number", "reference no", "instrument id", "instrument no",
        "cheque/reference no",
    ],
    "desc": [
        "description", "narration", "particulars", "details", "remarks",
        "transaction details", "transaction remarks",
        "narration / description", "description / narration",
        "transaction description", "descriptions",
    ],
    "debit": [
        "debit", "debit amount", "withdrawal", "withdrawal amt",
        "withdrawal (dr)", "withdrawals", "withdrawal amount", "debit(dr)",
        "debits", "dr",
    ],
    "credit": [
        "credit", "credit amount", "deposit", "deposit amt",
        "deposit (cr)", "deposits", "deposit amount", "credit(cr)",
        "credits", "cr",
    ],
    "amount": ["amount", "transaction amount", "amt", "txn amount", "amount (inr)"],
    "type": ["dr/cr", "cr/dr", "type", "txn type", "transaction type", "dr / cr", "cr / dr", "drcr"],
    "balance": [
        "balance", "closing balance", "running balance", "available balance",
        "balance (inr)", "bal", "closing bal",
    ],
}

# Resolution order: columns that are easy to identify unambiguously (ref
# numbers, dates, balance) are claimed first so a broader alias such as
# "amount" cannot swallow a column meant for something more specific.
FIELD_ORDER = ["ref", "value_date", "date", "balance", "debit", "credit", "type", "amount", "desc"]


def _norm_header(cell):
    s = str(cell or "").strip().lower()
    s = s.replace(".", "")
    s = re.sub(r"\s+", " ", s)
    return s


def _tokens(norm):
    return re.findall(r"[a-z0-9]+", norm)


def _resolve_columns(cells):
    """Map field name -> column index for one header row, exact matches
    winning over partial ones across every field before any field falls
    back to a substring or token match."""
    norm = [_norm_header(c) for c in cells]
    toks = [_tokens(n) for n in norm]
    claimed = set()
    mapping = {}

    for field in FIELD_ORDER:
        aliases = FIELD_ALIASES[field]
        for idx, n in enumerate(norm):
            if idx in claimed or not n:
                continue
            if n in aliases:
                claimed.add(idx)
                mapping[field] = idx
                break

    for field in FIELD_ORDER:
        if field in mapping:
            continue
        aliases = FIELD_ALIASES[field]
        for idx, n in enumerate(norm):
            if idx in claimed or not n:
                continue
            hit = False
            for alias in aliases:
                if len(alias) < 4:
                    if alias in toks[idx]:
                        hit = True
                        break
                elif alias in n:
                    hit = True
                    break
            if hit:
                claimed.add(idx)
                mapping[field] = idx
                break
    return mapping


def _score_header(cells):
    mapping = _resolve_columns(cells)
    has_amount = any(f in mapping for f in ("debit", "credit", "amount"))
    has_date = any(f in mapping for f in ("date", "value_date"))
    has_desc = "desc" in mapping
    if has_amount and (has_date or has_desc):
        return len(mapping), mapping
    return 0, mapping


def _detect_header(rows, max_scan=25):
    best_idx, best_score, best_mapping = None, 0, {}
    for i, row in enumerate(rows[:max_scan]):
        score, mapping = _score_header(row)
        if score > best_score:
            best_idx, best_score, best_mapping = i, score, mapping
    if best_idx is None:
        return None, {}
    return best_idx, best_mapping


# --- Bank detection --------------------------------------------------------- #
# IFSC bank codes (SBIN0, HDFC0, ...) are a reliable fingerprint when they
# appear anywhere in the letterhead or account block, so they are checked
# alongside the bank's plain name. When neither is present the header's own
# wording is matched against a short table of distinctive column phrases.

BANK_TEXT_MARKERS = [
    ("HDFC", ("hdfc bank", "hdfc0")),
    ("ICICI", ("icici bank", "icic0")),
    ("Axis", ("axis bank", "utib0")),
    ("Kotak", ("kotak mahindra", "kotak bank", "kkbk0")),
    ("IDFC First", ("idfc first", "idfb0")),
    ("IndusInd", ("indusind bank", "indb0")),
    ("Yes Bank", ("yes bank", "yesb0")),
    ("Bank of Baroda", ("bank of baroda", "barb0")),
    ("PNB", ("punjab national bank", "punb0")),
    ("Canara", ("canara bank", "cnrb0")),
    ("SBI", ("state bank of india", "sbin0")),
]

BANK_COLUMN_SIGNATURES = {
    "HDFC": ("chq/ref no", "withdrawal amt", "deposit amt"),
    "ICICI": ("transaction remarks", "withdrawal amount (inr)", "deposit amount (inr)"),
    "SBI": ("ref no/cheque no", "ref no./cheque no"),
    "Axis": ("tran date", "chq no", "particulars"),
    "Kotak": ("sl no", "chq / ref no"),
}


def _detect_bank_text(text):
    low = (text or "").lower()
    for bank, markers in BANK_TEXT_MARKERS:
        for marker in markers:
            if marker in low:
                return bank
    return "Unknown"


def _detect_bank(rows, header_idx, mapping):
    scan_upto = (header_idx if header_idx is not None else min(len(rows), 5)) + 1
    blob = " ".join(" ".join(r) for r in rows[:scan_upto])
    bank = _detect_bank_text(blob)
    if bank != "Unknown":
        return bank
    if header_idx is not None and header_idx < len(rows):
        header_norm = _norm_header(" ".join(rows[header_idx]))
        best_bank, best_hits = "Unknown", 0
        for bank_name, sigs in BANK_COLUMN_SIGNATURES.items():
            hits = sum(1 for s in sigs if s in header_norm)
            if hits > best_hits:
                best_bank, best_hits = bank_name, hits
        if best_hits >= 2:
            return best_bank
    return "Unknown"


# --- Noise rejection --------------------------------------------------------- #

_NOISE_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in [
        r"^opening balance", r"^closing balance", r"^balance\s*b/?f",
        r"^b/f\b", r"^c/f\b", r"brought forward", r"carried forward",
        r"^sub\s*-?\s*total", r"^grand\s*-?\s*total", r"^total\b",
        r"statement of account", r"^page\s*\d+", r"account statement",
        r"statement period", r"statement summary", r"computer generated",
        r"^ifsc", r"^micr", r"nomination registered", r"^\*+$", r"^-+$",
    ]
]
_NUMERIC_ONLY_RE = re.compile(r"^[\d.,\-\s]+$")


def _is_noise_desc(desc):
    d = (desc or "").strip()
    if not d:
        return False
    return any(p.search(d) for p in _NOISE_PATTERNS)


# --- Row accumulator --------------------------------------------------------- #

class _StatementBuilder:
    """Collects parsed rows, skip counts and human-readable warnings across
    a whole statement, and carries the running balance forward so a
    single-amount-column file without a Dr/Cr marker can still be split
    into credits and debits from the direction the balance moves."""

    def __init__(self):
        self.rows = []
        self.skipped = 0
        self.prev_balance = None
        self._notes = []
        self._notes_seen = set()
        self._counts = {}

    def note(self, msg):
        if msg not in self._notes_seen:
            self._notes_seen.add(msg)
            self._notes.append(msg)

    def bump(self, key, template):
        tmpl, n = self._counts.get(key, (template, 0))
        self._counts[key] = (tmpl, n + 1)

    def warnings(self):
        out = list(self._notes)
        for _, (tmpl, n) in self._counts.items():
            out.append(tmpl.format(n=n))
        return out

    def finalize(self, bank, source_format):
        return {
            "rows": self.rows,
            "bank": bank,
            "warnings": self.warnings(),
            "row_count": len(self.rows),
            "skipped": self.skipped,
            "source_format": source_format,
        }

    # -- table rows (CSV / XLSX / PDF tables) -- #

    def process_table(self, data_rows, mapping):
        for cells in data_rows:
            self._process_row(cells, mapping)

    def _cell(self, cells, mapping, field):
        idx = mapping.get(field)
        if idx is None or idx >= len(cells):
            return ""
        return cells[idx] or ""

    def _process_row(self, cells, mapping):
        desc_raw = self._cell(cells, mapping, "desc").strip()
        date_raw = self._cell(cells, mapping, "date").strip() or self._cell(cells, mapping, "value_date").strip()
        d = parse_date(date_raw) if date_raw else None
        if date_raw and d is None:
            self.bump("bad_date", "{n} row(s) had a date that could not be read and were left blank.")

        balance_amt = _signed_balance(self._cell(cells, mapping, "balance"))

        if desc_raw and _is_noise_desc(desc_raw):
            self.skipped += 1
            self.bump("noise", "{n} opening/closing-balance, total or statement-header row(s) skipped.")
            if balance_amt is not None:
                self.prev_balance = balance_amt
            return

        amount, txn_type = self._infer_amount(cells, mapping, balance_amt)

        if not desc_raw:
            self.skipped += 1
            if amount is None and d is None:
                self.bump("blank", "{n} blank row(s) skipped.")
            else:
                self.bump("empty_desc", "{n} row(s) skipped for having no description.")
            if balance_amt is not None:
                self.prev_balance = balance_amt
            return

        if _NUMERIC_ONLY_RE.match(desc_raw):
            self.skipped += 1
            self.bump("numeric_desc", "{n} row(s) skipped because the description was numeric only.")
            if balance_amt is not None:
                self.prev_balance = balance_amt
            return

        if amount is None:
            # No date and no readable amount on a row that still has text
            # is almost always a wrapped continuation of the previous
            # transaction's description in a PDF table.
            if self.rows and d is None:
                self._merge_into_last(desc_raw)
                return
            self.skipped += 1
            self.bump("no_amount", "{n} row(s) skipped because no amount could be read.")
            if balance_amt is not None:
                self.prev_balance = balance_amt
            return

        self.rows.append({
            "date": d,
            "raw_description": desc_raw[:300],
            "amount": round(float(amount), 2),
            "txn_type": txn_type,
            "balance": balance_amt,
        })
        if balance_amt is not None:
            self.prev_balance = balance_amt

    def _infer_amount(self, cells, mapping, balance_amt):
        if "debit" in mapping or "credit" in mapping:
            deb_amt, _ = parse_amount_signed(self._cell(cells, mapping, "debit")) if "debit" in mapping else (None, None)
            cred_amt, _ = parse_amount_signed(self._cell(cells, mapping, "credit")) if "credit" in mapping else (None, None)
            if cred_amt:
                return cred_amt, "credit"
            if deb_amt:
                return deb_amt, "debit"
            return None, None

        if "amount" in mapping:
            amt, sign = parse_amount_signed(self._cell(cells, mapping, "amount"))
            if not amt:
                return None, None
            txn_type = self._direction_from_type_column(cells, mapping)
            if txn_type is None and sign == -1:
                txn_type = "debit"
            elif txn_type is None and sign == 1:
                txn_type = "credit"
            if txn_type is None:
                txn_type = self._direction_from_balance(balance_amt)
            if txn_type is None:
                txn_type = "debit"
                self.bump("ambiguous_dir", "{n} row(s) had no debit/credit marker and no balance to infer "
                                            "direction from; assumed debit.")
            return amt, txn_type

        return None, None

    def _direction_from_type_column(self, cells, mapping):
        if "type" not in mapping:
            return None
        raw = _norm_header(self._cell(cells, mapping, "type"))
        if raw in ("dr", "debit", "d"):
            return "debit"
        if raw in ("cr", "credit", "c"):
            return "credit"
        return None

    def _direction_from_balance(self, new_balance):
        if new_balance is None or self.prev_balance is None:
            return None
        if new_balance > self.prev_balance + 0.005:
            return "credit"
        if new_balance < self.prev_balance - 0.005:
            return "debit"
        return None

    def _merge_into_last(self, text):
        if not self.rows:
            return
        prev = self.rows[-1]
        merged = (prev["raw_description"] + " " + text).strip()
        prev["raw_description"] = merged[:300]

    # -- PDF text-line fallback -- #

    def process_text_line(self, date_val, desc, tokens):
        parsed = [parse_amount_signed(t) for t in tokens]
        parsed = [p for p in parsed if p[0] is not None]
        if not parsed:
            self.skipped += 1
            self.bump("no_amount", "{n} row(s) skipped because no amount could be read.")
            return

        balance_amt = None
        if len(parsed) == 1:
            amt, sign = parsed[0]
        elif len(parsed) == 2:
            (amt, sign), (bamt, bsign) = parsed
            balance_amt = -bamt if bsign == -1 else bamt
        else:
            lead = parsed[:-1]
            nonzero_lead = [p for p in lead if p[0]]
            amt, sign = nonzero_lead[0] if nonzero_lead else lead[0]
            bamt, bsign = parsed[-1]
            balance_amt = -bamt if bsign == -1 else bamt

        if not amt:
            self.skipped += 1
            self.bump("no_amount", "{n} row(s) skipped because no amount could be read.")
            return

        desc = desc.strip()
        if not desc:
            self.skipped += 1
            self.bump("empty_desc", "{n} row(s) skipped for having no description.")
            if balance_amt is not None:
                self.prev_balance = balance_amt
            return

        txn_type = None
        if sign == -1:
            txn_type = "debit"
        elif sign == 1:
            txn_type = "credit"
        if txn_type is None:
            low = desc.lower()
            if re.search(r"\bcr\b|credit", low):
                txn_type = "credit"
            elif re.search(r"\bdr\b|debit", low):
                txn_type = "debit"
        if txn_type is None:
            txn_type = self._direction_from_balance(balance_amt)
        if txn_type is None:
            txn_type = "debit"
            self.bump("ambiguous_dir", "{n} row(s) had no debit/credit marker and no balance to infer "
                                        "direction from; assumed debit.")

        self.rows.append({
            "date": date_val,
            "raw_description": desc[:300],
            "amount": round(float(amt), 2),
            "txn_type": txn_type,
            "balance": balance_amt,
        })
        if balance_amt is not None:
            self.prev_balance = balance_amt

    def merge_text_continuation(self, line):
        self._merge_into_last(line)


# --- CSV / XLSX grid loading --------------------------------------------------- #

def _read_csv_grid(file_bytes):
    try:
        raw_df = pd.read_csv(io.BytesIO(file_bytes), header=None, dtype=str, keep_default_na=False)
        return [[("" if c is None else str(c)).strip() for c in row] for row in raw_df.values.tolist()]
    except Exception:
        text = file_bytes.decode("utf-8", errors="replace")
        grid = list(csv.reader(io.StringIO(text)))
        width = max((len(r) for r in grid), default=0)
        return [[(c or "").strip() for c in (r + [""] * (width - len(r)))] for r in grid]


def _parse_grid(rows_2d, source_format):
    builder = _StatementBuilder()
    header_idx, mapping = _detect_header(rows_2d)
    if header_idx is None:
        builder.note("Could not confidently detect the header row; assumed the first row is the header.")
        header_idx = 0
        mapping = _resolve_columns(rows_2d[0]) if rows_2d else {}
    bank = _detect_bank(rows_2d, header_idx, mapping)
    if "balance" not in mapping:
        builder.note("No closing balance column found; balance will be blank for these transactions.")
    data_rows = rows_2d[header_idx + 1:]
    builder.process_table(data_rows, mapping)
    return builder.finalize(bank=bank, source_format=source_format)


def _parse_csv(file_bytes):
    rows_2d = _read_csv_grid(file_bytes)
    return _parse_grid(rows_2d, "csv")


def _parse_excel(file_bytes):
    try:
        import openpyxl  # noqa: F401
    except ImportError:
        raise ValueError(
            "Reading Excel statements needs the 'openpyxl' package. Install it with: pip install openpyxl"
        )
    try:
        raw_df = pd.read_excel(io.BytesIO(file_bytes), header=None, dtype=str, engine="openpyxl")
    except ImportError:
        raise ValueError(
            "Reading Excel statements needs the 'openpyxl' package. Install it with: pip install openpyxl"
        )
    raw_df = raw_df.fillna("")
    rows_2d = [[str(c).strip() for c in row] for row in raw_df.values.tolist()]
    return _parse_grid(rows_2d, "xlsx")


# --- PDF parsing --------------------------------------------------------- #

_DATE_LEAD_RE = re.compile(
    r"^(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}-[A-Za-z]{3,9}-\d{2,4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4})\s+(.*)$"
)
_AMOUNT_TOKEN_RE = re.compile(r"[₹]?\(?-?\d[\d,]*\.\d{2}\)?(?:\s*(?:dr|cr))?", re.IGNORECASE)


def _parse_pdf_text_page(text, builder):
    if not text:
        return
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        m = _DATE_LEAD_RE.match(line)
        if not m:
            if builder.rows and not _is_noise_desc(line):
                builder.merge_text_continuation(line)
            continue
        date_str, rest = m.group(1), m.group(2).strip()
        d = parse_date(date_str)
        if _is_noise_desc(rest):
            builder.skipped += 1
            builder.bump("noise", "{n} opening/closing-balance, total or statement-header row(s) skipped.")
            tokens = _AMOUNT_TOKEN_RE.findall(rest)
            if tokens:
                bal = _signed_balance(tokens[-1])
                if bal is not None:
                    builder.prev_balance = bal
            continue
        tokens = _AMOUNT_TOKEN_RE.findall(rest)
        if not tokens:
            builder.skipped += 1
            builder.bump("no_amount", "{n} row(s) skipped because no amount could be read.")
            continue
        desc = rest
        for t in tokens:
            desc = desc.replace(t, " ", 1)
        desc = re.sub(r"\s+", " ", desc).strip()
        builder.process_text_line(d, desc, tokens)


def _clean_pdf_table(table):
    cleaned = [[("" if c is None else str(c)).strip() for c in row] for row in (table or [])]
    return [r for r in cleaned if any(cell for cell in r)]


def _parse_pdf(file_bytes, password):
    if not HAS_PDF:
        raise ValueError("PDF parsing needs the 'pdfplumber' package, which is not installed.")
    try:
        pdf_obj = pdfplumber.open(io.BytesIO(file_bytes), password=password)
    except Exception as exc:
        msg = str(exc).lower()
        type_name = type(exc).__name__.lower()
        if "password" in msg or "encrypt" in msg or "password" in type_name:
            if password:
                raise ValueError("The password entered for this PDF is incorrect. Please check it and try again.")
            raise ValueError(
                "This PDF statement is password protected. Please supply the statement password and upload again."
            )
        raise ValueError(f"Could not open the PDF file: {exc}")

    builder = _StatementBuilder()
    bank_guess = "Unknown"
    last_mapping, last_ncols = None, None

    with pdf_obj as pdf:
        text_blob = ""
        for page in pdf.pages[:3]:
            text_blob += (page.extract_text() or "") + "\n"
        bank_guess = _detect_bank_text(text_blob)

        for page in pdf.pages:
            tables = page.extract_tables() or []
            used_table = False
            for table in tables:
                cleaned = _clean_pdf_table(table)
                if len(cleaned) < 2:
                    continue
                header_idx, mapping = _detect_header(cleaned, max_scan=min(25, len(cleaned)))
                if mapping:
                    data_rows = cleaned[header_idx + 1:]
                    last_mapping, last_ncols = mapping, len(cleaned[0])
                elif last_mapping is not None and len(cleaned[0]) == last_ncols:
                    mapping = last_mapping
                    data_rows = cleaned
                    builder.note(
                        "Reused the column layout detected on an earlier page for a continuation "
                        "table that had no header row of its own."
                    )
                else:
                    continue
                if bank_guess == "Unknown":
                    bank_guess = _detect_bank(cleaned, header_idx if mapping is not last_mapping else None, mapping)
                if "balance" not in mapping:
                    builder.note("No closing balance column found; balance will be blank for these transactions.")
                builder.process_table(data_rows, mapping)
                used_table = True
            if not used_table:
                builder.note(
                    "Some pages had no ruled table pdfplumber could read; used line-by-line text parsing instead."
                )
                _parse_pdf_text_page(page.extract_text() or "", builder)

    return builder.finalize(bank=bank_guess, source_format="pdf")


# --- Public interface --------------------------------------------------- #

def parse_statement_detailed(filename, file_bytes, password=None):
    """Parse a bank statement and return rows plus bank, warnings and counts."""
    name = (filename or "").strip().lower()
    if name.endswith(".csv"):
        return _parse_csv(file_bytes)
    if name.endswith(".pdf"):
        return _parse_pdf(file_bytes, password)
    if name.endswith((".xlsx", ".xls")):
        return _parse_excel(file_bytes)
    raise ValueError("Unsupported file type. Please upload a PDF, CSV, or Excel (.xlsx) bank statement.")


def parse_statement(filename, file_bytes, password=None):
    """Parse a bank statement and return just the transaction rows."""
    return parse_statement_detailed(filename, file_bytes, password)["rows"]
