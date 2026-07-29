"""Web layer: authentication, access control and every page rendering."""
import io
import os
import tempfile

import pytest

import app as web
from models import db, User, Transaction
from conftest import SAMPLE_DIR


@pytest.fixture()
def client():
    """A logged-out test client against the scratch database that conftest
    selected before app.py was imported."""
    assert "smartedit_tests" in web.app.config["SQLALCHEMY_DATABASE_URI"], (
        "the tests are pointed at the real database")
    web.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, SECRET_KEY="test-key")
    with web.app.app_context():
        db.drop_all()
        db.create_all()
    with web.app.test_client() as c:
        yield c
    with web.app.app_context():
        db.session.remove()


def register(client, email="shyam@example.com", password="secret123"):
    return client.post("/register", data={"name": "Shyam", "email": email,
                                          "password": password},
                       follow_redirects=True)


PROTECTED = ["/dashboard", "/add", "/view", "/tracker", "/chat",
             "/salary", "/goals", "/budget", "/insights", "/export.csv"]


@pytest.mark.parametrize("path", PROTECTED)
def test_pages_require_a_login(client, path):
    response = client.get(path)
    assert response.status_code in (301, 302)
    assert "/login" in response.headers.get("Location", "")


@pytest.mark.parametrize("path", PROTECTED)
def test_every_page_renders_for_a_new_account_with_no_data(client, path):
    """A brand new user must never meet an error page."""
    register(client)
    assert client.get(path).status_code == 200


def test_registration_then_login(client):
    register(client)
    client.get("/logout")
    response = client.post("/login", data={"email": "shyam@example.com",
                                           "password": "secret123"},
                           follow_redirects=True)
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_a_wrong_password_is_refused(client):
    register(client)
    client.get("/logout")
    response = client.post("/login", data={"email": "shyam@example.com",
                                           "password": "wrong"},
                           follow_redirects=True)
    assert b"Invalid" in response.data


def test_the_same_email_cannot_register_twice(client):
    register(client)
    client.get("/logout")
    response = register(client)
    assert b"already exists" in response.data


def test_password_is_never_stored_in_the_clear(client):
    register(client)
    with web.app.app_context():
        stored = User.query.filter_by(email="shyam@example.com").first().password_hash
    assert "secret123" not in stored
    assert len(stored) > 40


def test_uploading_a_statement_imports_and_categorises_it(client):
    register(client)
    with open(os.path.join(SAMPLE_DIR, "sample_statement.csv"), "rb") as fh:
        data = {"statement": (io.BytesIO(fh.read()), "sample_statement.csv")}
    response = client.post("/upload", data=data,
                           content_type="multipart/form-data", follow_redirects=True)
    assert response.status_code == 200
    with web.app.app_context():
        rows = Transaction.query.all()
        assert len(rows) >= 25
        assert all(r.category for r in rows)
        assert all(r.fingerprint for r in rows)
        assert any(r.category == "Food & Dining" for r in rows)


def test_uploading_the_same_statement_twice_does_not_duplicate_it(client):
    register(client)
    path = os.path.join(SAMPLE_DIR, "sample_statement.csv")
    for _ in range(2):
        with open(path, "rb") as fh:
            client.post("/upload",
                        data={"statement": (io.BytesIO(fh.read()), "sample_statement.csv")},
                        content_type="multipart/form-data", follow_redirects=True)
    with web.app.app_context():
        assert Transaction.query.count() < 40, "the second upload was imported again"


def test_an_unreadable_file_is_reported_politely(client):
    register(client)
    response = client.post(
        "/upload", data={"statement": (io.BytesIO(b"not a statement"), "notes.txt")},
        content_type="multipart/form-data", follow_redirects=True)
    assert response.status_code == 200
    assert b"Traceback" not in response.data


def test_a_manual_entry_is_saved(client):
    register(client)
    client.post("/add", data={"amount": "1250", "description": "Chai and snacks",
                              "txn_type": "debit", "date": "2026-05-14",
                              "category": "Food & Dining"}, follow_redirects=True)
    with web.app.app_context():
        row = Transaction.query.filter_by(description="Chai and snacks").first()
        assert row is not None
        assert row.amount == 1250.0
        assert row.category == "Food & Dining"


def test_the_chat_endpoint_answers(client):
    register(client)
    with open(os.path.join(SAMPLE_DIR, "sample_statement.csv"), "rb") as fh:
        client.post("/upload",
                    data={"statement": (io.BytesIO(fh.read()), "sample_statement.csv")},
                    content_type="multipart/form-data", follow_redirects=True)
    response = client.post("/chat/send", json={"message": "how much did I spend on food"})
    assert response.status_code == 200
    assert response.json["reply"]


def test_an_empty_chat_message_is_handled(client):
    register(client)
    response = client.post("/chat/send", json={"message": "   "})
    assert response.status_code == 200
    assert response.json["reply"]


def test_a_salary_profile_is_saved_and_shown(client):
    register(client)
    response = client.post("/salary", data={"ctc_annual": "1800000", "regime": "new",
                                            "basic_pct": "40", "hra_pct": "50",
                                            "rent_paid_monthly": "0", "state": "Tamil Nadu",
                                            "pf_opt_in": "on"},
                           follow_redirects=True)
    assert response.status_code == 200
    with web.app.app_context():
        from models import SalaryProfile
        profile = SalaryProfile.query.first()
        assert profile is not None
        assert profile.ctc_annual == 1800000.0
        assert profile.regime == "new"
        assert profile.basic_pct == pytest.approx(0.40), "percentages must be stored as fractions"

    import salary
    expected = salary.compute_take_home(1800000, regime="new", state="Tamil Nadu",
                                        pf_opt_in=True)
    rendered = f"{expected['net_monthly']:,.0f}".encode()
    assert rendered in response.data, "the computed take-home is not shown on the page"


def test_a_savings_goal_is_created(client):
    register(client)
    response = client.post("/goals", data={"name": "Emergency fund",
                                           "target_amount": "300000",
                                           "target_date": "2027-06-30",
                                           "saved_amount": "50000"},
                           follow_redirects=True)
    assert response.status_code == 200
    assert b"Emergency fund" in response.data


def test_export_returns_a_csv(client):
    register(client)
    client.post("/add", data={"amount": "500", "description": "Coffee",
                              "txn_type": "debit", "date": "2026-05-14"},
                follow_redirects=True)
    response = client.get("/export.csv")
    assert response.status_code == 200
    assert "csv" in response.headers["Content-Type"]
    assert b"Coffee" in response.data


def test_one_account_cannot_read_or_delete_another_accounts_transaction(client):
    register(client, email="one@example.com")
    client.post("/add", data={"amount": "900", "description": "Private entry",
                              "txn_type": "debit", "date": "2026-05-14"},
                follow_redirects=True)
    with web.app.app_context():
        victim_id = Transaction.query.filter_by(description="Private entry").first().id
    client.get("/logout")
    register(client, email="two@example.com")

    assert b"Private entry" not in client.get("/view").data
    client.post(f"/delete/{victim_id}", follow_redirects=True)
    with web.app.app_context():
        assert Transaction.query.get(victim_id) is not None, "another user deleted the row"


def test_recategorising_a_transaction_sticks(client):
    register(client)
    client.post("/add", data={"amount": "700", "description": "Unknown vendor",
                              "txn_type": "debit", "date": "2026-05-14"},
                follow_redirects=True)
    with web.app.app_context():
        txn_id = Transaction.query.filter_by(description="Unknown vendor").first().id
    client.post(f"/update_category/{txn_id}", data={"category": "Health"},
                follow_redirects=True)
    with web.app.app_context():
        assert Transaction.query.get(txn_id).category == "Health"
