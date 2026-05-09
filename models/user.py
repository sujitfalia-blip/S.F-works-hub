from extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    phone = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
        index=True
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=True
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    role = db.Column(
        db.String(20),
        default="user",
        index=True
    )

    status = db.Column(
        db.String(20),
        default="active",
        index=True
    )

    # Referral system (self reference OK)
    referred_by = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=True
    )

    referrals = db.relationship(
        'User',
        foreign_keys=[referred_by],
        backref='referrer',
        lazy=True
    )

    controller_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=True
    )

    controller = db.relationship(
        'User',
        foreign_keys=[controller_id],
        backref='controlled_users',
        lazy=True
    )

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

    is_deleted = db.Column(
        db.Boolean,
        default=False,
        index=True
    )

    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)

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

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<User {self.id} - {self.phone}>"
