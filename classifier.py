"""India-aware transaction classifier.

Hybrid engine: a keyword rule table maps cryptic bank narrations (e.g.
"UPI-SWIGGY-OKAXIS-XXXX1234") to one of the canonical categories with full
confidence, and a small TF-IDF + logistic regression model, trained on a
seed corpus of realistic narrations, covers whatever the rules do not
recognise. Payment rails (UPI, NEFT, IMPS, ...) are only ever read as a
"Transfers" category once every merchant rule has had a chance to match,
since a UPI payment to a known merchant is that merchant's category, not a
generic transfer.
"""
import csv
import os
import re

try:
    import joblib
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline
    from sklearn.metrics import accuracy_score
    HAS_SKLEARN = True
except Exception:
    HAS_SKLEARN = False

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SEED_PATH = os.path.join(DATA_DIR, "category_seed.csv")
MODEL_PATH = os.path.join(DATA_DIR, "category_model.joblib")

CATEGORIES = [
    "Income", "Rent", "EMI / Loans", "Insurance", "Investments", "Subscriptions",
    "Food & Dining", "Groceries", "Transport", "Utilities", "Shopping", "Health",
    "Education", "Entertainment", "Travel", "Transfers", "Others",
]

CONFIDENCE_FLOOR = 0.35

# --- Rule tables ----------------------------------------------------------- #
# Only credit-side transactions are read against the income keywords, since
# a debit narration containing the word "refund" (for instance a merchant
# name) is not income. Transfers is deliberately kept out of this ordered
# dict and matched in its own pass after every other category, so a rail
# keyword can never outrank a merchant keyword that also matched.

INCOME_KEYWORDS = [
    "SALARY", "SAL CR", "STIPEND", "INTEREST", "INT.PD", "DIVIDEND",
    "REFUND", "CASHBACK", "REVERSAL", "BONUS", "INCENTIVE",
    "REIMBURSEMENT", "PF WITHDRAWAL", "PF CREDIT", "TDS REFUND",
    "INCOME TAX REFUND", "ITR REFUND",
]

CATEGORY_KEYWORDS = {
    "Income": INCOME_KEYWORDS,
    "Rent": [
        "RENT", "LANDLORD", "PG ", "HOSTEL", "HOUSE RENT", "RENTAL",
        "NOBROKER", "NESTAWAY", "RENTPAY", "MAGICBRICKS RENT",
    ],
    "EMI / Loans": [
        "EMI", "LOAN", "HOMELOAN", "HOME LOAN", "CARLOAN", "CAR LOAN",
        "BAJAJ FIN", "BAJAJ FINSERV", "HDB FIN", "HDB FINANCIAL",
        "ACHDR", "PERSONAL LOAN", "MONEYVIEW", "MONEYTAP", "CASHE",
        "KREDITBEE", "EARLYSALARY", "TATA CAPITAL", "LOAN EMI", "NBFC",
        "LENDINGKART", "PAYSENSE",
    ],
    "Insurance": [
        "LIC", "INSURANCE", "PREMIUM", "POLICY", "HDFC LIFE", "ICICI PRU",
        "ICICI PRUDENTIAL", "MAX LIFE", "STAR HEALTH", "BAJAJ ALLIANZ",
        "NIVA BUPA", "ACKO", "DIGIT INSURANCE", "GO DIGIT", "POLICYBAZAAR",
        "TATA AIG", "SBI LIFE", "RELIANCE GENERAL",
    ],
    "Investments": [
        "MUTUAL FUND", "MF ", "SIP", "ZERODHA", "GROWW", "UPSTOX",
        "ANGEL ONE", "ANGELONE", "KUVERA", "INDMONEY", "COIN", "NPS",
        "PPF", "RD ", "FD ", "ELSS", "DEMAT", "CDSL", "NSDL", "ETMONEY",
        "PAYTM MONEY", "SMALLCASE",
    ],
    "Subscriptions": [
        "NETFLIX", "PRIME VIDEO", "HOTSTAR", "JIOHOTSTAR", "SONYLIV",
        "SPOTIFY", "GAANA", "YOUTUBE PREMIUM", "YOUTUBE", "GOOGLE ONE",
        "GOOGLE *", "APPLE.COM", "ICLOUD", "ZEE5", "ADOBE", "CANVA",
        "CHATGPT", "OPENAI", "MICROSOFT 365", "OFFICE 365", "CULTFIT MEMBERSHIP",
        "ANYTIME FITNESS", "GOLDSGYM", "GYM MEMBERSHIP", "AMAZON MUSIC",
    ],
    "Food & Dining": [
        "SWIGGY FOOD", "ZOMATO", "DOMINO", "DOMINOS", "MCDONALD", "KFC",
        "RESTAURANT", "CAFE", "EATFIT", "FAASOS", "BIRYANI", "PIZZA",
        "BARBEQUE", "BEHROUZ", "WOW MOMO", "HALDIRAM", "THIRD WAVE",
        "CHAI POINT", "STARBUCKS", "CCD", "CAFE COFFEE DAY", "SUBWAY",
        "BURGER KING", "BOX8", "FRESHMENU", "SWIGGY",
    ],
    "Groceries": [
        "BIGBASKET", "BLINKIT", "ZEPTO", "SWIGGY INSTAMART", "INSTAMART",
        "DMART", "D-MART", "STAR BAZAAR", "SPENCERS", "NATURES BASKET",
        "LICIOUS", "COUNTRY DELIGHT", "GROFERS", "JIOMART",
        "RELIANCE FRESH", "RELIANCE RETAIL", "MORE SUPERMARKET",
        "GROCERY", "SUPERMARKET", "KIRANA", "MILKBASKET",
    ],
    "Transport": [
        "UBER", "OLA CABS", "RAPIDO", "NAMMA YATRI", "BLUSMART", "IRCTC",
        "REDBUS", "FASTAG", "SHELL", "NAYARA", "HPCL", "IOCL", "BPCL",
        "INDIAN OIL", "BMRCL", "CMRL", "DMRC", "FUEL", "PETROL", "DIESEL",
        "PARKING", "RAILWAY", "YULU", "BOUNCE", "OLA",
    ],
    "Utilities": [
        "TNEB", "BESCOM", "MSEB", "ADANI ELECTRICITY", "TATA POWER",
        "AIRTEL", "JIO", "VODAFONE", "VI ", "ACT FIBER", "ACT BROADBAND",
        "HATHWAY", "INDANE", "BHARATGAS", "BBPS", "ELECTRICITY", "EB ",
        "RECHARGE", "BROADBAND", "WATER BILL", "PIPED GAS", "DTH",
        "TATASKY", "D2H",
    ],
    "Shopping": [
        "AMAZON PAY", "AMAZON", "FLIPKART", "MYNTRA", "AJIO", "MEESHO",
        "NYKAA", "CROMA", "RELIANCE DIGITAL", "VIJAY SALES", "IKEA",
        "DECATHLON", "TATACLIQ", "SNAPDEAL", "LIFESTYLE", "PANTALOONS",
        "SHOPPERS STOP", "WESTSIDE", "MAX FASHION",
    ],
    "Health": [
        "APOLLO", "MEDPLUS", "PHARMEASY", "1MG", "NETMEDS", "PRACTO",
        "CULT.FIT", "CULTFIT", "PHARMACY", "HOSPITAL", "CLINIC",
        "DIAGNOSTIC", "PATHLAB", "DR LAL", "METROPOLIS", "THYROCARE",
        "DENTAL", "DOCTOR",
    ],
    "Education": [
        "UDEMY", "COURSERA", "UPGRAD", "UNACADEMY", "PHYSICSWALLAH",
        "SIMPLILEARN", "BITS PILANI", "COLLEGE FEE", "SCHOOL FEE",
        "TUITION", "UNIVERSITY", "EXAM FEE", "BYJU", "VEDANTU",
        "GREATLEARNING",
    ],
    "Entertainment": [
        "BOOKMYSHOW", "PVR", "INOX", "CINEMA", "STEAM", "PLAYSTATION",
        "DREAM11", "MPL", "GAMING", "XBOX",
    ],
    "Travel": [
        "MAKEMYTRIP", "GOIBIBO", "YATRA", "CLEARTRIP", "EASEMYTRIP",
        "OYO", "AIRBNB", "INDIGO", "VISTARA", "AIR INDIA", "AKASA",
        "SPICEJET", "HOTEL",
    ],
}

TRANSFER_KEYWORDS = [
    "UPI", "NEFT", "IMPS", "RTGS", "PAYTM", "PHONEPE", "GPAY", "GOOGLEPAY",
    "BHIM", "SENT TO", "TRANSFER", "P2P", "FUND TRANSFER", "A/C TRANSFER",
]

METHOD_MARKERS = [
    ("UPI", r"\bUPI\b"),
    ("NEFT", r"\bNEFT\b"),
    ("RTGS", r"\bRTGS\b"),
    ("IMPS", r"\bIMPS\b"),
    ("NACH", r"\bNACH\b"),
    ("ECS", r"\bECS\b"),
    ("ACH", r"\bACH\b"),
    ("ATM-CW", r"\bATM[-\s]?CW\b|\bATM\b"),
    ("POS", r"\bPOS\b"),
    ("EMI", r"\bEMI\b"),
    ("CARD", r"\bCARD\b"),
    ("INB", r"\bINB\b"),
    ("MB", r"\bMB\b"),
    ("CHQ", r"\bCHQ\b|\bCHEQUE\b"),
]

# Longest key wins, so a two-word phrase such as "RELIANCE FRESH" is
# preferred over a bare "RELIANCE" if both were ever present.
CANONICAL_NAMES = {
    "SWIGGY INSTAMART": "Swiggy Instamart", "SWIGGY": "Swiggy", "ZOMATO": "Zomato",
    "DOMINOS": "Dominos", "DOMINO": "Dominos", "MCDONALD": "McDonalds", "KFC": "KFC",
    "STARBUCKS": "Starbucks", "CAFE COFFEE DAY": "Cafe Coffee Day", "CCD": "Cafe Coffee Day",
    "HALDIRAM": "Haldiram's", "WOW MOMO": "Wow! Momo", "BEHROUZ": "Behrouz Biryani",
    "THIRD WAVE": "Third Wave Coffee", "CHAI POINT": "Chai Point", "SUBWAY": "Subway",
    "BURGER KING": "Burger King", "BOX8": "Box8", "FRESHMENU": "FreshMenu",
    "BIGBASKET": "BigBasket", "BLINKIT": "Blinkit", "ZEPTO": "Zepto",
    "DMART": "DMart", "D-MART": "DMart", "STAR BAZAAR": "Star Bazaar",
    "SPENCERS": "Spencer's", "NATURES BASKET": "Nature's Basket", "LICIOUS": "Licious",
    "COUNTRY DELIGHT": "Country Delight", "JIOMART": "JioMart",
    "RELIANCE FRESH": "Reliance Fresh", "MILKBASKET": "Milkbasket",
    "UBER": "Uber", "OLA CABS": "Ola", "OLA": "Ola", "RAPIDO": "Rapido",
    "NAMMA YATRI": "Namma Yatri", "BLUSMART": "BluSmart", "IRCTC": "IRCTC",
    "REDBUS": "RedBus", "FASTAG": "FASTag", "SHELL": "Shell", "NAYARA": "Nayara Energy",
    "HPCL": "HP Petrol Pump", "IOCL": "Indian Oil", "BPCL": "Bharat Petroleum",
    "INDIAN OIL": "Indian Oil", "YULU": "Yulu", "BOUNCE": "Bounce",
    "TNEB": "TNEB", "BESCOM": "BESCOM", "MSEB": "MSEB",
    "ADANI ELECTRICITY": "Adani Electricity", "TATA POWER": "Tata Power",
    "AIRTEL": "Airtel", "JIO": "Jio", "VODAFONE": "Vi", "ACT FIBER": "ACT Fibernet",
    "ACT BROADBAND": "ACT Fibernet", "HATHWAY": "Hathway", "INDANE": "Indane Gas",
    "BHARATGAS": "Bharat Gas", "TATASKY": "Tata Play",
    "AMAZON PAY": "Amazon Pay", "AMAZON": "Amazon", "FLIPKART": "Flipkart",
    "MYNTRA": "Myntra", "AJIO": "Ajio", "MEESHO": "Meesho", "NYKAA": "Nykaa",
    "CROMA": "Croma", "RELIANCE DIGITAL": "Reliance Digital", "VIJAY SALES": "Vijay Sales",
    "IKEA": "IKEA", "DECATHLON": "Decathlon", "TATACLIQ": "Tata CLiQ",
    "NETFLIX": "Netflix", "PRIME VIDEO": "Amazon Prime Video", "HOTSTAR": "Disney+ Hotstar",
    "JIOHOTSTAR": "JioHotstar", "SONYLIV": "SonyLIV", "SPOTIFY": "Spotify",
    "GAANA": "Gaana", "YOUTUBE PREMIUM": "YouTube Premium", "YOUTUBE": "YouTube",
    "GOOGLE ONE": "Google One", "ICLOUD": "iCloud", "ADOBE": "Adobe", "CANVA": "Canva",
    "CHATGPT": "ChatGPT", "OPENAI": "OpenAI",
    "APOLLO": "Apollo Pharmacy", "MEDPLUS": "MedPlus", "PHARMEASY": "PharmEasy",
    "1MG": "Tata 1mg", "NETMEDS": "Netmeds", "PRACTO": "Practo",
    "CULT.FIT": "cult.fit", "CULTFIT": "cult.fit", "DR LAL": "Dr Lal PathLabs",
    "METROPOLIS": "Metropolis Labs", "THYROCARE": "Thyrocare",
    "ZERODHA": "Zerodha", "GROWW": "Groww", "UPSTOX": "Upstox",
    "ANGEL ONE": "Angel One", "ANGELONE": "Angel One", "KUVERA": "Kuvera",
    "INDMONEY": "INDmoney", "ETMONEY": "ET Money", "PAYTM MONEY": "Paytm Money",
    "SMALLCASE": "Smallcase",
    "LIC": "LIC", "HDFC LIFE": "HDFC Life", "ICICI PRU": "ICICI Prudential",
    "ICICI PRUDENTIAL": "ICICI Prudential", "MAX LIFE": "Max Life Insurance",
    "STAR HEALTH": "Star Health Insurance", "BAJAJ ALLIANZ": "Bajaj Allianz",
    "NIVA BUPA": "Niva Bupa", "ACKO": "Acko", "DIGIT INSURANCE": "Go Digit Insurance",
    "GO DIGIT": "Go Digit Insurance", "POLICYBAZAAR": "PolicyBazaar",
    "TATA AIG": "Tata AIG", "SBI LIFE": "SBI Life",
    "MAKEMYTRIP": "MakeMyTrip", "GOIBIBO": "Goibibo", "YATRA": "Yatra",
    "CLEARTRIP": "Cleartrip", "EASEMYTRIP": "EaseMyTrip", "OYO": "OYO",
    "AIRBNB": "Airbnb", "INDIGO": "IndiGo", "VISTARA": "Vistara",
    "AIR INDIA": "Air India", "AKASA": "Akasa Air", "SPICEJET": "SpiceJet",
    "UDEMY": "Udemy", "COURSERA": "Coursera", "UPGRAD": "upGrad",
    "UNACADEMY": "Unacademy", "PHYSICSWALLAH": "Physics Wallah",
    "SIMPLILEARN": "Simplilearn", "BYJU": "BYJU'S", "VEDANTU": "Vedantu",
    "BOOKMYSHOW": "BookMyShow", "PVR": "PVR Cinemas", "INOX": "INOX",
    "STEAM": "Steam", "PLAYSTATION": "PlayStation", "DREAM11": "Dream11", "MPL": "MPL",
    "BAJAJ FINSERV": "Bajaj Finserv", "BAJAJ FIN": "Bajaj Finance",
    "HDB FINANCIAL": "HDB Financial Services", "HDB FIN": "HDB Financial Services",
    "MONEYVIEW": "MoneyView", "MONEYTAP": "MoneyTap", "KREDITBEE": "KreditBee",
    "EARLYSALARY": "EarlySalary", "TATA CAPITAL": "Tata Capital",
    "NOBROKER": "NoBroker", "NESTAWAY": "Nestaway",
}


# --- Helpers ------------------------------------------------------------- #

_BANK_HANDLE_RE = re.compile(r"@[a-z]+\b", re.IGNORECASE)
_MASKED_DIGITS_RE = re.compile(r"\b[X\*]{2,}\d*\b", re.IGNORECASE)
_LONG_REF_RE = re.compile(r"\b\d{6,}\b")
_RAIL_PREFIX_RE = re.compile(
    r"(?i)^(upi|neft|imps|rtgs|nach|ecs|ach|pos|atm|chq|inb|mb|card|emi)[\s\-/]+"
)

# Statements often follow the rail with a single-letter direction marker, as in
# "ACH-D-" or "NEFT-DR-". It carries no merchant information.
_DIRECTION_MARKER_RE = re.compile(r"(?i)^(dr|cr|d|c)[\s\-/]+")


def _strip_rail_and_refs(raw):
    """Remove the payment-rail prefix, bank handles (@okaxis, @ybl, ...),
    masked card/account digits and long reference numbers so what remains
    is the merchant or counterparty name."""
    s = (raw or "").strip()
    s = _RAIL_PREFIX_RE.sub("", s)
    s = _DIRECTION_MARKER_RE.sub("", s)
    s = _BANK_HANDLE_RE.sub("", s)
    s = _MASKED_DIGITS_RE.sub("", s)
    s = _LONG_REF_RE.sub("", s)
    return s


def clean_description(raw):
    """Turn a cryptic bank narration into a readable label."""
    if not raw:
        return "Transaction"
    s = _strip_rail_and_refs(raw)
    s = re.sub(r"[-_/|]+", " ", s)
    s = _strip_upi_handles(s)
    s = re.sub(r"\s+", " ", s).strip()
    cleaned = s.title()[:120]
    return cleaned if cleaned else "Transaction"


# A UPI narration carries the payer's bank handle, which tells the user nothing
# about what they bought, so it is dropped from the readable label.
# Only handles that are never a merchant name in their own right are listed
# here. Names such as Airtel or Paytm double as payees, so removing them would
# throw away the very word that identifies the transaction.
_UPI_HANDLES = re.compile(
    r"\b(?:ok(?:sbi|hdfc|icici|axis|bizaxis)|ybl|ibl|axl|apl|yesb|okbizaxis)\b",
    re.IGNORECASE)

# Terminal and reference numbers left behind by POS and UPI narrations.
_LOOSE_REFS = re.compile(r"\b\d{3,}\b")


def _strip_upi_handles(text):
    text = _UPI_HANDLES.sub(" ", text or "")
    return _LOOSE_REFS.sub(" ", text)


def detect_method(raw):
    """Identify the payment rail from a raw narration."""
    d = (raw or "").upper()
    for name, pattern in METHOD_MARKERS:
        if re.search(pattern, d):
            return name
    return "MANUAL"


def merchant_name(raw):
    """Normalise a raw narration to a canonical merchant display name."""
    if not raw:
        return "Unknown"
    text = _strip_rail_and_refs(raw).upper()
    best_key, best_len = None, 0
    for key in CANONICAL_NAMES:
        if key in text and len(key) > best_len:
            best_key, best_len = key, len(key)
    if best_key:
        return CANONICAL_NAMES[best_key]
    cleaned = clean_description(raw)
    words = [w for w in cleaned.split() if w]
    return " ".join(words[:3]) if words else "Transaction"


def _kw_hit(text, kw):
    """Substring match for a keyword four characters or longer; a shorter
    keyword (e.g. "RD ", "EMI") is required to sit on a word boundary so it
    cannot fire on an unrelated word such as "CARD" or "PREMIUM"."""
    k = kw.strip()
    if not k:
        return False
    if len(k) < 4:
        return re.search(r"(?<![A-Z0-9])" + re.escape(k) + r"(?![A-Z0-9])", text) is not None
    return kw in text


def _rule_classify(description, txn_type):
    d = (description or "").upper()
    stripped = _strip_rail_and_refs(d).upper()

    if txn_type == "credit":
        for kw in INCOME_KEYWORDS:
            if _kw_hit(d, kw):
                return "Income"

    for category, keywords in CATEGORY_KEYWORDS.items():
        if category == "Income":
            continue
        for kw in keywords:
            if _kw_hit(stripped, kw) or _kw_hit(d, kw):
                return category

    for kw in TRANSFER_KEYWORDS:
        if _kw_hit(d, kw):
            return "Transfers"

    return None


def classify(description, txn_type="debit", amount=None):
    """Return a single category for a raw transaction description."""
    return classify_with_confidence(description, txn_type, amount)[0]


def classify_with_confidence(description, txn_type="debit", amount=None):
    """Return (category, confidence, source). Rules run first and, when
    they fire, are trusted completely; the model only sees what the rules
    could not place."""
    rule_cat = _rule_classify(description, txn_type)
    if rule_cat is not None:
        return rule_cat, 1.0, "rule"

    if model_ready():
        cat, conf = _model_predict(description)
        if conf < CONFIDENCE_FLOOR:
            return "Others", conf, "model"
        return cat, conf, "model"

    return ("Income" if txn_type == "credit" else "Others"), 0.0, "rule"


# --- Model training / loading --------------------------------------------- #

_MODEL = None


def _load_seed_rows():
    rows = []
    with open(SEED_PATH, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append((r["description"], r["category"]))
    return rows


def _load_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    if not HAS_SKLEARN or not os.path.exists(MODEL_PATH):
        return None
    try:
        _MODEL = joblib.load(MODEL_PATH)
    except Exception:
        _MODEL = None
    return _MODEL


def _model_predict(description):
    model = _load_model()
    if model is None:
        return "Others", 0.0
    proba = model.predict_proba([description or ""])[0]
    idx = proba.argmax()
    return model.classes_[idx], float(proba[idx])


def model_ready():
    """True when scikit-learn is installed and a trained model is on disk."""
    if not HAS_SKLEARN:
        return False
    return _load_model() is not None


def train_model(rows=None):
    """Train the TF-IDF + logistic regression classifier and persist it.

    rows, when given, is a list of (description, category) pairs; otherwise
    the bundled seed corpus at data/category_seed.csv is used. Returns the
    held-out accuracy and the number of training samples.
    """
    if not HAS_SKLEARN:
        raise RuntimeError(
            "Training the category model needs scikit-learn and joblib. "
            "Install them with: pip install scikit-learn joblib"
        )
    data = rows if rows is not None else _load_seed_rows()
    texts = [d for d, _ in data]
    labels = [c for _, c in data]

    x_train, x_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5))),
        ("clf", LogisticRegression(max_iter=1000)),
    ])
    pipeline.fit(x_train, y_train)
    accuracy = float(accuracy_score(y_test, pipeline.predict(x_test)))

    os.makedirs(DATA_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    global _MODEL
    _MODEL = pipeline
    return {"accuracy": accuracy, "samples": len(data)}
