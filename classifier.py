"""India-aware transaction classifier.

Hybrid rule engine: keyword patterns map cryptic bank descriptions
(e.g. 'UPI-SWIGGY-OKAXIS-XXXX') to human categories. Unknown -> 'Others'.
"""
import re

# Order matters: more specific categories first.
CATEGORY_RULES = [
    ("Income",        ["SALARY", "SAL CR", "STIPEND", "INTEREST", "INT.PD", "DIVIDEND",
                       "REFUND", "CASHBACK", "REVERSAL"]),
    ("Rent",          ["RENT", "LANDLORD", "PG ", "HOSTEL"]),
    ("Insurance",     ["LIC", "INSURANCE", "PREMIUM", "POLICY", "HDFC LIFE", "MAX LIFE",
                       "STAR HEALTH", "BAJAJ ALLIANZ"]),
    ("EMI / Loans",   ["EMI", "LOAN", "HOMELOAN", "CARLOAN", "BAJAJ FIN", "HDB FIN",
                       "FINANCIAL", "ACHDR"]),
    ("Investments",   ["MUTUAL FUND", "MF ", "SIP", "ZERODHA", "GROWW", "UPSTOX", "NPS",
                       "PPF", "RD ", "FD ", "ELSS"]),
    ("Subscriptions", ["NETFLIX", "PRIME", "SPOTIFY", "HOTSTAR", "JIOHOTSTAR", "SONYLIV",
                       "YOUTUBE", "GOOGLE *", "APPLE.COM", "ZEE5", "ICLOUD", "ADOBE"]),
    ("Food & Dining", ["SWIGGY", "ZOMATO", "DOMINO", "MCDONALD", "KFC", "RESTAURANT",
                       "CAFE", "EATFIT", "FAASOS", "BIRYANI", "PIZZA", "BARBEQUE"]),
    ("Groceries",     ["BIGBASKET", "DMART", "D-MART", "RELIANCE FRESH", "RELIANCE RETAIL",
                       "GROFERS", "BLINKIT", "ZEPTO", "JIOMART", "MORE SUPERMARKET",
                       "GROCERY", "SUPERMARKET", "KIRANA"]),
    ("Transport",     ["UBER", "OLA", "RAPIDO", "IRCTC", "REDBUS", "FUEL", "PETROL",
                       "DIESEL", "HPCL", "IOCL", "BPCL", "INDIAN OIL", "METRO", "FASTAG",
                       "PARKING", "RAILWAY"]),
    ("Utilities",     ["ELECTRICITY", "EB ", "TNEB", "BESCOM", "RECHARGE", "AIRTEL",
                       "JIO", "VODAFONE", "VI ", "BROADBAND", "ACT FIBER", "WATER BILL",
                       "GAS", "INDANE", "BHARATGAS", "DTH", "TATASKY", "BBPS"]),
    ("Shopping",      ["AMAZON", "FLIPKART", "MYNTRA", "AJIO", "MEESHO", "NYKAA",
                       "TATACLIQ", "SNAPDEAL", "DECATHLON", "LIFESTYLE", "PANTALOONS",
                       "SHOPPERS STOP", "IKEA", "CROMA"]),
    ("Health",        ["PHARMACY", "APOLLO", "MEDPLUS", "PHARMEASY", "1MG", "NETMEDS",
                       "HOSPITAL", "CLINIC", "DIAGNOSTIC", "LAB", "DOCTOR", "DENTAL"]),
    ("Education",     ["UDEMY", "COURSERA", "BYJU", "UNACADEMY", "TUITION", "SCHOOL FEE",
                       "COLLEGE", "UNIVERSITY", "EXAM FEE"]),
    ("Entertainment", ["BOOKMYSHOW", "PVR", "INOX", "CINEMA", "GAMING", "STEAM",
                       "PLAYSTATION", "DREAM11"]),
    ("Travel",        ["MAKEMYTRIP", "GOIBIBO", "YATRA", "CLEARTRIP", "OYO", "AIRBNB",
                       "INDIGO", "VISTARA", "AIR INDIA", "SPICEJET", "HOTEL"]),
    ("Transfers",     ["UPI", "NEFT", "IMPS", "RTGS", "PAYTM", "PHONEPE", "GPAY",
                       "GOOGLEPAY", "BHIM", "SENT TO", "TRANSFER", "P2P"]),
]

METHOD_MARKERS = ["UPI", "NEFT", "NACH", "IMPS", "RTGS", "POS", "ATM", "CHQ", "ACH"]


def detect_method(description):
    d = (description or "").upper()
    for m in METHOD_MARKERS:
        if m in d:
            return m
    return "MANUAL"


def classify(description, txn_type="debit"):
    """Return a human category for a raw transaction description."""
    d = (description or "").upper()

    if txn_type == "credit":
        for kw in ("SALARY", "SAL CR", "STIPEND", "INTEREST", "DIVIDEND",
                   "REFUND", "CASHBACK", "INT.PD"):
            if kw in d:
                return "Income"

    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in d:
                if category == "Income" and txn_type == "debit":
                    continue
                return category

    if txn_type == "credit":
        return "Income"
    return "Others"


def clean_description(raw):
    """Make a readable label from a cryptic bank string."""
    if not raw:
        return "Transaction"
    s = re.sub(r"\b[X*]{3,}\d*\b", "", raw)
    s = re.sub(r"\b\d{6,}\b", "", s)
    s = re.sub(r"[-_/|]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    cleaned = s.title()[:120]
    return cleaned if cleaned else "Transaction"
