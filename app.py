"""SmartEdit AI — Flask application entry point."""
import os
from datetime import datetime, date
from collections import defaultdict
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import db, User, Transaction, ChatHistory
import parser as statement_parser
import classifier
import advisor
import rag

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# --------------------------------------------------------------------------- #
#  Auth helpers
# --------------------------------------------------------------------------- #
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def current_user():
    uid = session.get("user_id")
    return User.query.get(uid) if uid else None


# --------------------------------------------------------------------------- #
#  Auth routes
# --------------------------------------------------------------------------- #
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not (name and email and password):
            flash("All fields are required.", "error")
            return render_template("register.html")
        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
            return render_template("register.html")
        user = User(name=name, email=email,
                    password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        session["user_name"] = user.name
        return redirect(url_for("dashboard"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# --------------------------------------------------------------------------- #
#  Analytics helpers
# --------------------------------------------------------------------------- #
def month_summary(user_id, ref=None):
    ref = ref or date.today()
    txns = Transaction.query.filter_by(user_id=user_id).all()
    # Use the latest month present in data if current month is empty.
    months = sorted({(t.date.year, t.date.month) for t in txns if t.date}, reverse=True)
    target = (ref.year, ref.month)
    if months and target not in months:
        target = months[0]

    income = expense = 0.0
    cat_totals = defaultdict(float)
    for t in txns:
        if t.date and (t.date.year, t.date.month) == target:
            if t.txn_type == "credit":
                income += t.amount
            else:
                expense += t.amount
                cat_totals[t.category] += t.amount
    savings = income - expense
    rate = (savings / income * 100) if income else 0
    top = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)
    month_label = date(target[0], target[1], 1).strftime("%B %Y")
    return {
        "income": income, "expense": expense, "savings": savings,
        "savings_rate": rate, "top_categories": top, "month": month_label,
        "category_totals": dict(cat_totals),
    }


# --------------------------------------------------------------------------- #
#  Dashboard
# --------------------------------------------------------------------------- #
@app.route("/dashboard")
@login_required
def dashboard():
    uid = session["user_id"]
    has_data = Transaction.query.filter_by(user_id=uid).count() > 0
    summary = month_summary(uid)
    recent = (Transaction.query.filter_by(user_id=uid)
              .order_by(Transaction.date.desc(), Transaction.id.desc())
              .limit(8).all())
    advice = advisor.generate_advice(summary) if has_data else ""
    chart = {
        "labels": [c for c, _ in summary["top_categories"]],
        "values": [round(a, 2) for _, a in summary["top_categories"]],
    }
    return render_template("dashboard.html", summary=summary, recent=recent,
                           has_data=has_data, advice=advice, chart=chart)


# --------------------------------------------------------------------------- #
#  Upload + manual add
# --------------------------------------------------------------------------- #
@app.route("/upload", methods=["POST"])
@login_required
def upload():
    uid = session["user_id"]
    file = request.files.get("statement")
    if not file or not file.filename:
        flash("Please choose a file to upload.", "error")
        return redirect(url_for("dashboard"))
    try:
        rows = statement_parser.parse_statement(file.filename, file.read())
    except Exception as e:
        flash(f"Could not read the file: {e}", "error")
        return redirect(url_for("dashboard"))

    added = 0
    for r in rows:
        raw = r["raw_description"]
        cat = classifier.classify(raw, r["txn_type"])
        txn = Transaction(
            user_id=uid,
            date=r["date"] or date.today(),
            description=classifier.clean_description(raw),
            raw_description=raw,
            amount=r["amount"],
            txn_type=r["txn_type"],
            category=cat,
            method=classifier.detect_method(raw),
            source="upload",
        )
        db.session.add(txn)
        db.session.flush()
        rag.index_transaction(txn)
        added += 1
    db.session.commit()
    flash(f"Imported {added} transactions from {file.filename}.", "success")
    return redirect(url_for("view"))


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    uid = session["user_id"]
    if request.method == "POST":
        try:
            amount = abs(float(request.form.get("amount", 0)))
        except ValueError:
            flash("Enter a valid amount.", "error")
            return redirect(url_for("add"))
        desc = request.form.get("description", "").strip() or "Manual entry"
        txn_type = request.form.get("txn_type", "debit")
        d = request.form.get("date")
        category = request.form.get("category", "").strip()
        if not category:
            category = classifier.classify(desc, txn_type)
        txn = Transaction(
            user_id=uid,
            date=datetime.strptime(d, "%Y-%m-%d").date() if d else date.today(),
            description=desc, raw_description=desc, amount=amount,
            txn_type=txn_type, category=category,
            method="MANUAL", source="manual",
        )
        db.session.add(txn)
        db.session.flush()
        rag.index_transaction(txn)
        db.session.commit()
        flash("Entry added.", "success")
        return redirect(url_for("view"))
    return render_template("add.html", categories=CATEGORIES, today=date.today().isoformat())


# --------------------------------------------------------------------------- #
#  View / database
# --------------------------------------------------------------------------- #
@app.route("/view")
@login_required
def view():
    uid = session["user_id"]
    cat = request.args.get("category", "")
    ttype = request.args.get("type", "")
    q = Transaction.query.filter_by(user_id=uid)
    if cat:
        q = q.filter_by(category=cat)
    if ttype:
        q = q.filter_by(txn_type=ttype)
    txns = q.order_by(Transaction.date.desc(), Transaction.id.desc()).all()
    total_in = sum(t.amount for t in txns if t.txn_type == "credit")
    total_out = sum(t.amount for t in txns if t.txn_type == "debit")
    cats = sorted({t.category for t in Transaction.query.filter_by(user_id=uid).all()})
    return render_template("view.html", txns=txns, categories=cats,
                           sel_cat=cat, sel_type=ttype,
                           total_in=total_in, total_out=total_out,
                           all_categories=CATEGORIES)


@app.route("/update_category/<int:txn_id>", methods=["POST"])
@login_required
def update_category(txn_id):
    uid = session["user_id"]
    txn = Transaction.query.filter_by(id=txn_id, user_id=uid).first_or_404()
    txn.category = request.form.get("category", txn.category)
    rag.index_transaction(txn)
    db.session.commit()
    return redirect(url_for("view"))


@app.route("/delete/<int:txn_id>", methods=["POST"])
@login_required
def delete_txn(txn_id):
    uid = session["user_id"]
    txn = Transaction.query.filter_by(id=txn_id, user_id=uid).first_or_404()
    db.session.delete(txn)
    db.session.commit()
    return redirect(url_for("view"))


# --------------------------------------------------------------------------- #
#  Tracker
# --------------------------------------------------------------------------- #
@app.route("/tracker")
@login_required
def tracker():
    uid = session["user_id"]
    txns = Transaction.query.filter_by(user_id=uid).all()
    daily = defaultdict(lambda: {"credit": 0.0, "debit": 0.0})
    monthly = defaultdict(lambda: {"credit": 0.0, "debit": 0.0})
    weekday = defaultdict(lambda: {"credit": 0.0, "debit": 0.0})
    wd_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for t in txns:
        if not t.date:
            continue
        daily[t.date.isoformat()][t.txn_type] += t.amount
        monthly[t.date.strftime("%Y-%m")][t.txn_type] += t.amount
        weekday[wd_names[t.date.weekday()]][t.txn_type] += t.amount

    daily_sorted = sorted(daily.items())[-30:]
    monthly_sorted = sorted(monthly.items())
    data = {
        "daily": {
            "labels": [d for d, _ in daily_sorted],
            "credit": [round(v["credit"], 2) for _, v in daily_sorted],
            "debit": [round(v["debit"], 2) for _, v in daily_sorted],
        },
        "monthly": {
            "labels": [m for m, _ in monthly_sorted],
            "credit": [round(v["credit"], 2) for _, v in monthly_sorted],
            "debit": [round(v["debit"], 2) for _, v in monthly_sorted],
        },
        "weekday": {
            "labels": wd_names,
            "debit": [round(weekday[w]["debit"], 2) for w in wd_names],
        },
    }
    return render_template("tracker.html", data=data,
                           has_data=len(txns) > 0)


# --------------------------------------------------------------------------- #
#  Chat
# --------------------------------------------------------------------------- #
@app.route("/chat")
@login_required
def chat():
    uid = session["user_id"]
    history = (ChatHistory.query.filter_by(user_id=uid)
               .order_by(ChatHistory.created_at).all())
    return render_template("chat.html", history=history)


@app.route("/chat/send", methods=["POST"])
@login_required
def chat_send():
    uid = session["user_id"]
    msg = (request.json or {}).get("message", "").strip()
    if not msg:
        return jsonify({"reply": "Please type a question."})
    db.session.add(ChatHistory(user_id=uid, role="user", message=msg))
    reply = rag.answer(uid, msg)
    db.session.add(ChatHistory(user_id=uid, role="assistant", message=reply))
    db.session.commit()
    return jsonify({"reply": reply})


CATEGORIES = [
    "Income", "Rent", "EMI / Loans", "Insurance", "Investments", "Subscriptions",
    "Food & Dining", "Groceries", "Transport", "Utilities", "Shopping", "Health",
    "Education", "Entertainment", "Travel", "Transfers", "Others",
]


@app.context_processor
def inject_globals():
    return {"user_name": session.get("user_name"),
            "provider": Config.LLM_PROVIDER}


if __name__ == "__main__":
    app.run(debug=True, port=5000)
