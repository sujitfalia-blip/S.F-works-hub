from extensions import db
from datetime import datetime


class Work(db.Model):

    __tablename__ = "works"

    # =========================
    # PRIMARY KEY
    # =========================
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =========================
    # WORK INFO
    # =========================
    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    workers = db.Column(
        db.String(100)
    )

    salary = db.Column(
        db.String(100)
    )

    date = db.Column(
        db.String(100)
    )

    time = db.Column(
        db.String(100)
    )

    phone = db.Column(
        db.String(20)
    )

    location = db.Column(
        db.String(200)
    )

    # =========================
    # USER RELATION
    # =========================
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=True
    )

    # =========================
    # STATUS
    # =========================
    status = db.Column(
        db.String(20),
        default="active",
        nullable=False,
        index=True
    )

    is_deleted = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True
    )

    # =========================
    # TIMESTAMPS
    # =========================
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # =========================
    # DEBUG
    # =========================
    def __repr__(self):
        return f"<Work {self.title}>"
