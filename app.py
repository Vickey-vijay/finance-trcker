"""SmartEdit AI — Flask application entry point."""
import csv
import io
import os
from datetime import datetime, date
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, jsonify, Response)
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config, BASE_DIR
from models import db, User, Transaction, ChatHistory, SalaryProfile, SavingsGoal, Budget, ensure_schema
import parser as statement_parser
import classifier
from classifier import CATEGORIES
import advisor
import analytics
import salary
import rag
import llm_local

app = Flask(__name__)
app.config.from_object(Config)


def _load_or_create_secret_key():
    """Keep the session signing key stable across restarts.

    A key supplied via the environment is used as-is. Otherwise a random key
    is generated once and cached next to the database, so redeploying or
    restarting the server does not invalidate every user's session.
    """
    env_key = os.environ.get("SECRET_KEY")
    if env_key:
        return env_key
    key_path = os.path.join(BASE_DIR, ".secret_key")
    if os.path.exists(key_path):
        with open(key_path, "r", encoding="utf-8") as f:
            stored = f.read().strip()
        if stored:
            return stored
    new_key = os.urandom(32).hex()
    os.makedirs(os.path.dirname(key_path), exist_ok=True)
    with open(key_path, "w", encoding="utf-8") as f:
        f.write(new_key)
    return new_key


app.config["SECRET_KEY"] = _load_or_create_secret_key()
db.init_app(app)

with app.app_context():
    db.create_all()
    ensure_schema(db.engine)
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
#  Dashboard
# --------------------------------------------------------------------------- #
@app.route("/dashboard")
@login_required
def dashboard():
    uid = session["user_id"]
    has_data = Transaction.query.filter_by(user_id=uid).count() > 0
    summary = analytics.month_summary(uid)
    recent = (Transaction.query.filter_by(user_id=uid)
              .order_by(Transaction.date.desc(), Transaction.id.desc())
              .limit(8).all())
    advice = advisor.generate_advice(summary) if has_data else ""
    chart = {
        "labels": [c for c, _ in summary["top_categories"]],
        "values": [round(a, 2) for _, a in summary["top_categories"]],
    }
    mom = analytics.month_over_month(uid, months=6) if has_data else []
    insights = analytics.spending_insights(uid) if has_data else []
    trend_chart = {
        "labels": [m["label"] for m in mom],
        "income": [round(m["income"], 2) for m in mom],
        "expense": [round(m["expense"], 2) for m in mom],
    }
    return render_template("dashboard.html", summary=summary, recent=recent,
                           has_data=has_data, advice=advice, chart=chart,
                           trend_chart=trend_chart, insights=insights[:4])


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
    password = request.form.get("pdf_password") or None
    try:
        parsed = statement_parser.parse_statement_detailed(
            file.filename, file.read(), password=password)
    except Exception as e:
        flash(f"Could not read the file: {e}", "error")
        return redirect(url_for("dashboard"))

    added = 0
    duplicates = 0
    for r in parsed["rows"]:
        raw = r["raw_description"]
        txn_date = r["date"] or date.today()
        fingerprint = Transaction.make_fingerprint(
            uid, txn_date, r["amount"], r["txn_type"], raw)
        already_exists = Transaction.query.filter_by(
            user_id=uid, fingerprint=fingerprint).first()
        if already_exists:
            duplicates += 1
            continue
        category, confidence, _source = classifier.classify_with_confidence(
            raw, r["txn_type"], r["amount"])
        txn = Transaction(
            user_id=uid,
            date=txn_date,
            description=classifier.clean_description(raw),
            raw_description=raw,
            amount=r["amount"],
            txn_type=r["txn_type"],
            category=category,
            confidence=confidence,
            method=classifier.detect_method(raw),
            merchant=classifier.merchant_name(raw),
            balance=r.get("balance"),
            source="upload",
            fingerprint=fingerprint,
        )
        db.session.add(txn)
        db.session.flush()
        rag.index_transaction(txn)
        added += 1
    db.session.commit()

    bank = parsed.get("bank", "Unknown")
    summary_msg = f"{bank} statement: imported {added} transaction(s)"
    if duplicates:
        summary_msg += f", skipped {duplicates} duplicate(s)"
    summary_msg += "."
    flash(summary_msg, "success")
    for warning in parsed.get("warnings", []):
        flash(warning, "error")
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
        if d:
            try:
                txn_date = datetime.strptime(d, "%Y-%m-%d").date()
            except ValueError:
                flash("Enter a valid date.", "error")
                return redirect(url_for("add"))
        else:
            txn_date = date.today()
        category = request.form.get("category", "").strip()
        if not category:
            category = classifier.classify(desc, txn_type)
        txn = Transaction(
            user_id=uid,
            date=txn_date,
            description=desc, raw_description=desc, amount=amount,
            txn_type=txn_type, category=category, confidence=1.0,
            merchant=classifier.merchant_name(desc),
            method="MANUAL", source="manual",
        )
        txn.fingerprint = Transaction.make_fingerprint(
            uid, txn.date, amount, txn_type, desc)
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
    search = request.args.get("q", "").strip()
    q = Transaction.query.filter_by(user_id=uid)
    if cat:
        q = q.filter_by(category=cat)
    if ttype:
        q = q.filter_by(txn_type=ttype)
    if search:
        q = q.filter(Transaction.description.ilike(f"%{search}%"))
    txns = q.order_by(Transaction.date.desc(), Transaction.id.desc()).all()
    total_in = sum(t.amount for t in txns if t.txn_type == "credit")
    total_out = sum(t.amount for t in txns if t.txn_type == "debit")
    cats = sorted({t.category for t in Transaction.query.filter_by(user_id=uid).all()})
    return render_template("view.html", txns=txns, categories=cats,
                           sel_cat=cat, sel_type=ttype, search=search,
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


@app.route("/export.csv")
@login_required
def export_csv():
    uid = session["user_id"]
    txns = (Transaction.query.filter_by(user_id=uid)
            .order_by(Transaction.date.desc(), Transaction.id.desc()).all())
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Date", "Description", "Merchant", "Category", "Type",
                     "Amount", "Method", "Balance"])
    for t in txns:
        writer.writerow([
            t.date.isoformat() if t.date else "", t.description, t.merchant or "",
            t.category, t.txn_type, f"{t.amount:.2f}", t.method or "",
            f"{t.balance:.2f}" if t.balance is not None else "",
        ])
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=transactions.csv"})


# --------------------------------------------------------------------------- #
#  Tracker
# --------------------------------------------------------------------------- #
@app.route("/tracker")
@login_required
def tracker():
    uid = session["user_id"]
    has_data = Transaction.query.filter_by(user_id=uid).count() > 0
    data = analytics.trends(uid)
    return render_template("tracker.html", data=data, has_data=has_data)


# --------------------------------------------------------------------------- #
#  Salary and tax
# --------------------------------------------------------------------------- #
@app.route("/salary", methods=["GET", "POST"])
@login_required
def salary_page():
    uid = session["user_id"]
    profile = SalaryProfile.query.filter_by(user_id=uid).first()
    if request.method == "POST":
        try:
            ctc = float(request.form.get("ctc_annual", 0))
            basic_pct = float(request.form.get("basic_pct", 40)) / 100.0
            hra_pct = float(request.form.get("hra_pct", 50)) / 100.0
            rent_monthly = float(request.form.get("rent_paid_monthly", 0) or 0)
            other_allowances = float(request.form.get("other_allowances", 0) or 0)
        except ValueError:
            flash("Please enter valid numbers for the salary details.", "error")
            return redirect(url_for("salary_page"))
        metro = request.form.get("metro") == "on"
        pf_opt_in = request.form.get("pf_opt_in") == "on"
        regime = request.form.get("regime", "new")
        state = request.form.get("state", "Tamil Nadu")

        if profile is None:
            profile = SalaryProfile(user_id=uid)
            db.session.add(profile)
        profile.ctc_annual = ctc
        profile.basic_pct = basic_pct
        profile.hra_pct = hra_pct
        profile.metro = metro
        profile.rent_paid_monthly = rent_monthly
        profile.regime = regime
        profile.other_allowances = other_allowances
        profile.pf_opt_in = pf_opt_in
        profile.state = state
        db.session.commit()
        flash("Salary profile saved.", "success")
        return redirect(url_for("salary_page"))

    breakdown = None
    comparison = None
    if profile:
        kwargs = dict(
            ctc_annual=profile.ctc_annual, basic_pct=profile.basic_pct,
            hra_pct=profile.hra_pct, metro=profile.metro,
            rent_paid_monthly=profile.rent_paid_monthly, regime=profile.regime,
            other_allowances=profile.other_allowances, pf_opt_in=profile.pf_opt_in,
            state=profile.state,
        )
        breakdown = salary.compute_take_home(**kwargs)
        comparison = salary.compare_regimes(**kwargs)
    return render_template("salary.html", profile=profile, breakdown=breakdown,
                           comparison=comparison)


# --------------------------------------------------------------------------- #
#  Savings goals
# --------------------------------------------------------------------------- #
@app.route("/goals", methods=["GET", "POST"])
@login_required
def goals():
    uid = session["user_id"]
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        try:
            target_amount = float(request.form.get("target_amount", 0))
        except ValueError:
            flash("Enter a valid target amount.", "error")
            return redirect(url_for("goals"))
        target_date_raw = request.form.get("target_date")
        target_date = None
        if target_date_raw:
            try:
                target_date = datetime.strptime(target_date_raw, "%Y-%m-%d").date()
            except ValueError:
                flash("Enter a valid target date.", "error")
                return redirect(url_for("goals"))
        if not name or not target_date:
            flash("A goal needs a name and a target date.", "error")
            return redirect(url_for("goals"))
        goal = SavingsGoal(user_id=uid, name=name, target_amount=target_amount,
                           target_date=target_date)
        db.session.add(goal)
        db.session.commit()
        flash("Goal created.", "success")
        return redirect(url_for("goals"))

    summary = analytics.month_summary(uid)
    monthly_surplus = max(summary["savings"], 0.0)
    rows = SavingsGoal.query.filter_by(user_id=uid).order_by(
        SavingsGoal.created_at.desc()).all()
    projections = {}
    for g in rows:
        projections[g.id] = salary.goal_projection(
            g.target_amount, g.target_date, g.saved_amount, monthly_surplus)
    return render_template("goals.html", goals=rows, projections=projections,
                           monthly_surplus=monthly_surplus)


@app.route("/goals/<int:goal_id>/delete", methods=["POST"])
@login_required
def delete_goal(goal_id):
    uid = session["user_id"]
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=uid).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    return redirect(url_for("goals"))


@app.route("/goals/<int:goal_id>/save", methods=["POST"])
@login_required
def update_goal_savings(goal_id):
    uid = session["user_id"]
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=uid).first_or_404()
    try:
        goal.saved_amount = max(float(request.form.get("saved_amount", goal.saved_amount)), 0.0)
    except ValueError:
        flash("Enter a valid amount saved.", "error")
        return redirect(url_for("goals"))
    if goal.saved_amount >= goal.target_amount:
        goal.status = "achieved"
    db.session.commit()
    return redirect(url_for("goals"))


# --------------------------------------------------------------------------- #
#  Budgets
# --------------------------------------------------------------------------- #
@app.route("/budget", methods=["GET", "POST"])
@login_required
def budget():
    uid = session["user_id"]
    if request.method == "POST":
        category = request.form.get("category", "")
        try:
            limit = float(request.form.get("monthly_limit", 0))
        except ValueError:
            flash("Enter a valid monthly limit.", "error")
            return redirect(url_for("budget"))
        existing = Budget.query.filter_by(user_id=uid, category=category).first()
        if existing:
            existing.monthly_limit = limit
        else:
            db.session.add(Budget(user_id=uid, category=category, monthly_limit=limit))
        db.session.commit()
        flash("Budget saved.", "success")
        return redirect(url_for("budget"))

    status = analytics.budget_status(uid)
    return render_template("budget.html", status=status, categories=CATEGORIES)


# --------------------------------------------------------------------------- #
#  Insights
# --------------------------------------------------------------------------- #
@app.route("/insights")
@login_required
def insights():
    uid = session["user_id"]
    return render_template(
        "insights.html",
        spending_insights=analytics.spending_insights(uid),
        subscriptions=analytics.recurring_subscriptions(uid),
        top_merchants=analytics.top_merchants(uid),
        month_over_month=analytics.month_over_month(uid),
    )


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
    result = rag.answer_detailed(uid, msg)
    db.session.add(ChatHistory(user_id=uid, role="assistant", message=result["reply"]))
    db.session.commit()
    return jsonify(result)


@app.context_processor
def inject_globals():
    return {"user_name": session.get("user_name"),
            "provider": advisor.provider_status()["detail"],
            "model_ready": llm_local.is_available()}


if __name__ == "__main__":
    # use_reloader=False avoids the reloader's parent/child process pair,
    # which on Windows makes Ctrl+C delivery to the console unpredictable.
    # Catching KeyboardInterrupt here means a deliberate Ctrl+C exits with
    # code 0 instead of STATUS_CONTROL_C_EXIT, so cmd.exe does not treat a
    # normal shutdown as a broken batch job (see run.bat).
    try:
        app.run(debug=False, port=5000, use_reloader=False)
    except KeyboardInterrupt:
        pass
