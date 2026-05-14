from extensions import db
from datetime import datetime


class Booking(db.Model):

    __tablename__ = "booking"

    # =========================
    # PRIMARY KEY
    # =========================
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =========================
    # RELATIONS
    # =========================
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False,
        index=True
    )

    # IMPORTANT FIX
    # work.id ❌
    # works.id ✅
    work_id = db.Column(
        db.Integer,
        db.ForeignKey('works.id'),
        nullable=False,
        index=True
    )

    # =========================
    # ORM RELATIONSHIPS
    # =========================
    user = db.relationship(
        'User',
        backref=db.backref(
            'bookings',
            lazy=True
        )
    )

    work = db.relationship(
        'Work',
        backref=db.backref(
            'bookings',
            lazy=True
        )
    )

    # =========================
    # STATUS CONTROL
    # =========================
    status = db.Column(
        db.String(20),
        default="pending",
        nullable=False,
        index=True
    )
    # pending / approved / rejected / blocked / deleted

    # =========================
    # ACTIVE CONTROL
    # =========================
    is_active = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True
    )

    # =========================
    # ACTION TRACKING
    # =========================
    approved_by = db.Column(
        db.Integer,
        nullable=True,
        index=True
    )

    rejected_by = db.Column(
        db.Integer,
        nullable=True,
        index=True
    )

    blocked_by = db.Column(
        db.Integer,
        nullable=True,
        index=True
    )

    deleted_by = db.Column(
        db.Integer,
        nullable=True,
        index=True
    )

    # =========================
    # REJECTION INFO
    # =========================
    reject_reason = db.Column(
        db.Text,
        nullable=True
    )

    # =========================
    # USER MESSAGE
    # =========================
    message = db.Column(
        db.Text,
        nullable=True
    )

    # =========================
    # SOFT DELETE
    # =========================
    is_deleted = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True
    )

    # =========================
    # AUDIT LOG
    # =========================
    action_log = db.Column(
        db.Text,
        nullable=True
    )

    # =========================
    # TIMESTAMPS
    # =========================
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # =========================
    # PREVENT DUPLICATE BOOKING
    # =========================
    __table_args__ = (
        db.UniqueConstraint(
            'user_id',
            'work_id',
            name='unique_booking'
        ),
    )

    # =========================
    # DEBUG / ADMIN VIEW
    # =========================
    def __repr__(self):
        return f"<Booking {self.id}>"
