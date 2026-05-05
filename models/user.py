from extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    # 🔐 AUTH
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)

    # 👤 BASIC INFO
    name = db.Column(db.String(100), nullable=False, index=True)

    # 👑 ROLE SYSTEM
    role = db.Column(db.String(20), default="user", index=True)
    # user / admin / super_admin / owner

    # 🟢 ACCOUNT STATUS
    status = db.Column(db.String(20), default="active", index=True)
    # active / blocked / pending

    # 🔗 REFERRAL SYSTEM
    referred_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    referrals = db.relationship(
        'User',
        backref=db.backref('referrer', remote_side=[id]),
        lazy=True
    )

    # 🎯 CONTROL SYSTEM
    controller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    controller = db.relationship(
        'User',
        foreign_keys=[controller_id],
        lazy=True
    )

    # 📍 WORK FILTER
    skill = db.Column(db.String(100), index=True)
    area = db.Column(db.String(100), index=True)

    # 🗑 SOFT DELETE
    is_deleted = db.Column(db.Boolean, default=False, index=True)

    # 📜 AUDIT
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)

    # 🟢 REALTIME PRESENCE
    is_online = db.Column(db.Boolean, default=False, index=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    socket_id = db.Column(db.String(100), nullable=True)

    # 🕒 TIMESTAMP
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
