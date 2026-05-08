from extensions import db
from datetime import datetime

class Work(db.Model):
    __tablename__ = "work"

    id = db.Column(db.Integer, primary_key=True)

    # 📌 Basic Info (FIXED NAME: workers)
    title = db.Column(db.String(200), nullable=False)
    workers = db.Column(db.Integer, nullable=False)
    salary = db.Column(db.Integer, nullable=False)

    # 📅 Date & Time
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)

    # 📱 Contact
    phone = db.Column(db.String(20), nullable=False)

    # 👤 Creator
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # 🔥 STATUS
    status = db.Column(db.String(20), default="pending", index=True)
    is_active = db.Column(db.Boolean, default=False)

    # 🕒 TIMESTAMP
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
