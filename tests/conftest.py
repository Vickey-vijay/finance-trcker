"""Shared fixtures. Every database test runs against a throwaway SQLite file
so the tests can never disturb the real smartedit.db."""
import os
import sys
import tempfile
from datetime import date

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Point the application at a scratch database before anything imports app.py.
# Flask-SQLAlchemy binds its engine when init_app runs, so overriding the URI
# afterwards would silently leave the tests writing to the real smartedit.db.
TEST_DB = os.path.join(tempfile.gettempdir(), "smartedit_tests.db")
os.environ["SMARTEDIT_DATABASE_URI"] = "sqlite:///" + TEST_DB

from flask import Flask                      # noqa: E402
from models import db, User, Transaction, ensure_schema   # noqa: E402
import classifier                            # noqa: E402

SAMPLE_DIR = os.path.join(ROOT, "sample_data")


@pytest.fixture()
def app_ctx():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True
    db.init_app(app)
    with app.app_context():
        db.create_all()
        ensure_schema(db.engine)
        yield app
        db.session.remove()
    try:
        os.remove(path)
    except OSError:
        pass


@pytest.fixture()
def user(app_ctx):
    u = User(name="Test User", email="test@example.com", password_hash="x")
    db.session.add(u)
    db.session.commit()
    return u


def add_txn(user_id, day, description, amount, txn_type="debit", category=None):
    """Insert one transaction, classifying it the way the upload route does."""
    cat, confidence, _source = classifier.classify_with_confidence(description, txn_type, amount)
    t = Transaction(
        user_id=user_id, date=day,
        description=classifier.clean_description(description),
        raw_description=description, amount=amount, txn_type=txn_type,
        category=category or cat, merchant=classifier.merchant_name(description),
        confidence=confidence, method=classifier.detect_method(description),
        source="upload",
    )
    t.fingerprint = Transaction.make_fingerprint(user_id, day, amount, txn_type, description)
    db.session.add(t)
    return t


@pytest.fixture()
def seeded(app_ctx, user):
    """A month of realistic activity for one user."""
    rows = [
        (date(2026, 5, 1), "SALARY CREDIT ACME TECH PVT LTD", 68000.0, "credit"),
        (date(2026, 5, 2), "UPI-SWIGGY-OKAXIS-XXXX1234", 420.0, "debit"),
        (date(2026, 5, 3), "NACH-LIC PREMIUM-AUTODEBIT", 2150.0, "debit"),
        (date(2026, 5, 4), "POS-4521-RELIANCE FRESH", 1840.0, "debit"),
        (date(2026, 5, 5), "NEFT-DR-RENT TRANSFER LANDLORD", 18000.0, "debit"),
        (date(2026, 5, 6), "UPI-ZOMATO-OKICICI-XXXX5678", 560.0, "debit"),
        (date(2026, 5, 7), "NETFLIX SUBSCRIPTION", 649.0, "debit"),
        (date(2026, 5, 9), "UPI-UBER INDIA-OKHDFC-9988", 310.0, "debit"),
        (date(2026, 5, 12), "BBPS TNEB ELECTRICITY BILL", 1430.0, "debit"),
        (date(2026, 5, 15), "ACH-D- HDB FINANCIAL-CARLOAN EMI", 9500.0, "debit"),
        (date(2026, 5, 18), "SIP ZERODHA COIN MUTUAL FUND", 5000.0, "debit"),
        (date(2026, 5, 20), "UPI-BIGBASKET-OKAXIS-1122", 2480.0, "debit"),
        (date(2026, 6, 1), "SALARY CREDIT ACME TECH PVT LTD", 68000.0, "credit"),
        (date(2026, 6, 5), "NEFT-DR-RENT TRANSFER LANDLORD", 18000.0, "debit"),
        (date(2026, 6, 7), "NETFLIX SUBSCRIPTION", 649.0, "debit"),
        (date(2026, 6, 8), "UPI-SWIGGY-OKAXIS-XXXX7788", 655.0, "debit"),
        (date(2026, 6, 12), "BBPS TNEB ELECTRICITY BILL", 1510.0, "debit"),
        (date(2026, 6, 15), "ACH-D- HDB FINANCIAL-CARLOAN EMI", 9500.0, "debit"),
    ]
    for day, desc, amt, kind in rows:
        add_txn(user.id, day, desc, amt, kind)
    db.session.commit()
    return user
