from extensions import db
from datetime import datetime


class Work(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # 📌 Basic Info
    title = db.Column(db.String(200), nullable=False)
    workers_needed = db.Column(db.Integer, nullable=False)
    salary = db.Column(db.Integer, nullable=False)

    # 📅 Date & Time
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)

    # 📱 Contact
    phone = db.Column(db.String(20), nullable=False)

    # 👤 Creator
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # 🔥 STATUS CONTROL
    status = db.Column(db.String(20), default="pending", index=True)
    is_active = db.Column(db.Boolean, default=False)

    # 👑 TRACKING
    approved_by = db.Column(db.Integer, nullable=True)
    rejected_by = db.Column(db.Integer, nullable=True)
    edited_by = db.Column(db.Integer, nullable=True)

    reject_reason = db.Column(db.Text)

    # 🗑 SOFT DELETE
    is_deleted = db.Column(db.Boolean, default=False)

    # 📝 VERSION
    edit_count = db.Column(db.Integer, default=0)

    # 🕒 TIMESTAMPS
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
