"""Database models (SQLAlchemy)."""
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

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
        }


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
