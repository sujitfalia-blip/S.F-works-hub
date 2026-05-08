from extensions import db
from datetime import datetime

class Work(db.Model):
    __tablename__ = "work"

    id = db.Column(db.Integer, primary_key=True)

    # ================= BASIC =================
    title = db.Column(db.String(200), nullable=False)
    workers = db.Column(db.Integer, nullable=False)
    salary = db.Column(db.Float, nullable=False)

    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    # ================= STATUS =================
    status = db.Column(db.String(20), default="active")

    # 🔥 IMPORTANT FIX (your error fix)
    is_deleted = db.Column(db.Boolean, default=False, index=True)

    # ================= AUDIT =================
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Work {self.id} - {self.title}>"
