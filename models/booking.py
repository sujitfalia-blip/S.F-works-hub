from extensions import db
from datetime import datetime


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # 🔗 RELATIONS
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    work_id = db.Column(db.Integer, db.ForeignKey('work.id'), nullable=False, index=True)

    user = db.relationship('User', backref='bookings')
    work = db.relationship('Work', backref='bookings')

    # 📊 STATUS CONTROL
    status = db.Column(
        db.String(20),
        default="pending",
        index=True
    )
    # pending / approved / rejected / blocked / deleted

    # ⚡ ACTIVE CONTROL (clean version)
    is_active = db.Column(db.Boolean, default=False, index=True)

    # 👑 ACTION TRACKING
    approved_by = db.Column(db.Integer, nullable=True, index=True)
    rejected_by = db.Column(db.Integer, nullable=True, index=True)
    blocked_by = db.Column(db.Integer, nullable=True, index=True)
    deleted_by = db.Column(db.Integer, nullable=True, index=True)

    # 📝 REJECTION INFO
    reject_reason = db.Column(db.Text, nullable=True)

    # 💬 USER MESSAGE
    message = db.Column(db.Text, nullable=True)

    # 🗑 SOFT DELETE (SaaS SAFE)
    is_deleted = db.Column(db.Boolean, default=False, index=True)

    # 📜 AUDIT LOG (future use)
    action_log = db.Column(db.Text, nullable=True)

    # 🕒 TIMESTAMPS
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        index=True
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # 🚫 PREVENT DUPLICATE APPLICATION
    __table_args__ = (
        db.UniqueConstraint('user_id', 'work_id', name='unique_booking'),
    )
    
