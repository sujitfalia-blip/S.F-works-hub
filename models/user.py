from extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "user"

    # =========================================================
    # 🔑 PRIMARY KEY
    # =========================================================
    id = db.Column(db.Integer, primary_key=True)

    # =========================================================
    # 🔐 AUTH
    # =========================================================
    phone = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
        index=True
    )

    user = db.relationship('User', backref='profile', uselist=False)

    email = db.Column(
    db.String(120),
    unique=True,
    nullable=True
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    # =========================================================
    # 👤 BASIC INFO
    # =========================================================
    name = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    # =========================================================
    # 👑 ROLE SYSTEM
    # =========================================================
    role = db.Column(
        db.String(20),
        default="user",
        index=True
    )
    # user / admin / super_admin / owner

    # =========================================================
    # 🟢 ACCOUNT STATUS
    # =========================================================
    status = db.Column(
        db.String(20),
        default="active",
        index=True
    )
    # active / pending / blocked

    # =========================================================
    # 🔗 REFERRAL SYSTEM
    # =========================================================
    referred_by = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=True
    )

    referrals = db.relationship(
        'User',
        foreign_keys=[referred_by],
        backref=db.backref(
            'referrer',
            remote_side=[id]
        ),
        lazy=True
    )

    # =========================================================
    # 🎯 CONTROL SYSTEM
    # =========================================================
    controller_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=True,
        index=True
    )

    controller = db.relationship(
        'User',
        foreign_keys=[controller_id],
        remote_side=[id],
        backref='controlled_users',
        lazy=True
    )

    # =========================================================
    # 📍 WORK FILTER
    # =========================================================
    skill = db.Column(
        db.String(100),
        nullable=True,
        index=True
    )

    area = db.Column(
        db.String(100),
        nullable=True,
        index=True
    )

    # =========================================================
    # 🗑 SOFT DELETE
    # =========================================================
    is_deleted = db.Column(
        db.Boolean,
        default=False,
        index=True
    )

    # =========================================================
    # 📜 AUDIT
    # =========================================================
    created_by = db.Column(
        db.Integer,
        nullable=True
    )

    updated_by = db.Column(
        db.Integer,
        nullable=True
    )

    # =========================================================
    # 🟢 REALTIME SYSTEM
    # =========================================================
    is_online = db.Column(
        db.Boolean,
        default=False,
        index=True
    )

    last_seen = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    socket_id = db.Column(
        db.String(100),
        nullable=True
    )

    # =========================================================
    # 🕒 TIMESTAMPS
    # =========================================================
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # =========================================================
    # 🧠 DEBUG
    # =========================================================
    def __repr__(self):
        return f"<User {self.id} - {self.phone}>"
