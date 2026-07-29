"""Database models (SQLAlchemy)."""
import hashlib
import re
from datetime import datetime, date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship("Transaction", backref="user", cascade="all, delete-orphan")
    chats = db.relationship("ChatHistory", backref="user", cascade="all, delete-orphan")


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    date = db.Column(db.Date, default=date.today, index=True)
    description = db.Column(db.String(300), nullable=False)
    raw_description = db.Column(db.String(300))
    amount = db.Column(db.Float, nullable=False)          # always positive
    txn_type = db.Column(db.String(10), nullable=False)   # 'credit' or 'debit'
    category = db.Column(db.String(60), default="Others", index=True)
    method = db.Column(db.String(20))                     # UPI/NEFT/NACH/POS/IMPS/MANUAL
    source = db.Column(db.String(20), default="manual")   # upload / manual
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Statement re-upload de-duplication and reporting extensions.
    fingerprint = db.Column(db.String(64), index=True)
    merchant = db.Column(db.String(120), index=True)
    confidence = db.Column(db.Float, default=1.0)
    balance = db.Column(db.Float)

    embedding = db.relationship("Embedding", backref="transaction",
                                uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "description": self.description,
            "amount": self.amount,
            "txn_type": self.txn_type,
            "category": self.category,
            "method": self.method,
            "source": self.source,
            "merchant": self.merchant,
            "confidence": self.confidence,
            "balance": self.balance,
        }

    @staticmethod
    def make_fingerprint(user_id, txn_date, amount, txn_type, raw_description):
        """Stable identity for a statement row, used to skip duplicate re-uploads.

        The digest is over the fields that together identify one real-world
        transaction: which user, which day, how much, credit or debit, and the
        bank's own description text. Values are normalised first so that the
        same transaction produces the same fingerprint however it is re-parsed.
        """
        date_part = txn_date.isoformat() if txn_date else ""
        amount_part = f"{round(float(amount), 2):.2f}"
        desc_part = re.sub(r"\s+", " ", (raw_description or "").strip()).upper()
        payload = "|".join([str(user_id), date_part, amount_part,
                            (txn_type or ""), desc_part])
        return hashlib.sha1(payload.encode("utf-8")).hexdigest()


class Embedding(db.Model):
    __tablename__ = "embeddings"
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey("transactions.id"),
                               nullable=False, index=True)
    vector = db.Column(db.Text)  # JSON list of floats


class ChatHistory(db.Model):
    __tablename__ = "chat_history"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    role = db.Column(db.String(12), nullable=False)  # user / assistant
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SalaryProfile(db.Model):
    __tablename__ = "salary_profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    ctc_annual = db.Column(db.Float, nullable=False)
    basic_pct = db.Column(db.Float, default=0.40)
    hra_pct = db.Column(db.Float, default=0.50)
    metro = db.Column(db.Boolean, default=False)
    rent_paid_monthly = db.Column(db.Float, default=0.0)
    regime = db.Column(db.String(10), default="new")
    other_allowances = db.Column(db.Float, default=0.0)
    pf_opt_in = db.Column(db.Boolean, default=True)
    state = db.Column(db.String(40), default="Tamil Nadu")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SavingsGoal(db.Model):
    __tablename__ = "savings_goals"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    target_date = db.Column(db.Date)
    saved_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="active")


class Budget(db.Model):
    __tablename__ = "budgets"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    category = db.Column(db.String(60), nullable=False)
    monthly_limit = db.Column(db.Float, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "category", name="uq_budget_user_category"),
    )


# --------------------------------------------------------------------------- #
#  Schema upgrade helper
# --------------------------------------------------------------------------- #
def _add_column_ddl(column, dialect):
    """Render a single ADD COLUMN clause for a model column."""
    col_type = column.type.compile(dialect=dialect)
    clause = f'"{column.name}" {col_type}'
    default = column.default
    if default is not None and getattr(default, "is_scalar", False):
        value = default.arg
        if isinstance(value, bool):
            clause += f" DEFAULT {int(value)}"
        elif isinstance(value, (int, float)):
            clause += f" DEFAULT {value}"
        elif isinstance(value, str):
            clause += f" DEFAULT '{value}'"
    return clause


def ensure_schema(engine):
    """Bring an existing SQLite database up to date with the current models.

    New installs get every table from a plain ``create_all``. An existing
    ``smartedit.db`` predating this schema is missing the newer Transaction
    columns and the salary/goal/budget tables; those are added with
    ``ALTER TABLE`` so that rows already on disk are kept untouched. The
    function inspects the live database before acting, so calling it again
    on an already-upgraded database is a no-op.
    """
    db.metadata.create_all(engine)
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    dialect = engine.dialect

    for table in db.metadata.sorted_tables:
        if table.name not in existing_tables:
            continue
        existing_columns = {c["name"] for c in inspector.get_columns(table.name)}
        for column in table.columns:
            if column.name in existing_columns:
                continue
            ddl = _add_column_ddl(column, dialect)
            with engine.begin() as conn:
                conn.execute(text(f'ALTER TABLE "{table.name}" ADD COLUMN {ddl}'))
            if column.index or column.unique:
                index_name = f"ix_{table.name}_{column.name}"
                with engine.begin() as conn:
                    conn.execute(text(
                        f'CREATE INDEX IF NOT EXISTS "{index_name}" '
                        f'ON "{table.name}" ("{column.name}")'
                    ))
