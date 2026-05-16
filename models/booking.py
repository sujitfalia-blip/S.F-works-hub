from extensions import db
from datetime import datetime


class Booking(db.Model):

    __tablename__ = "bookings"

    # =========================================
    # PRIMARY KEY
    # =========================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =========================================
    # BOOKING USERS
    # =========================================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        index=True
    )

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        index=True
    )

    # =========================================
    # WORK INFO
    # =========================================

    work_id = db.Column(
        db.Integer,
        db.ForeignKey("works.id"),
        nullable=False,
        index=True
    )

    # =========================================
    # BOOKING DETAILS
    # =========================================

    booking_date = db.Column(
        db.String(50)
    )

    booking_time = db.Column(
        db.String(50)
    )

    address = db.Column(
        db.Text
    )

    notes = db.Column(
        db.Text
    )

    price = db.Column(
        db.Float,
        default=0
    )

    # =========================================
    # STATUS
    # =========================================

    status = db.Column(
        db.String(20),
        default="pending",
        nullable=False
    )
    # pending
    # accepted
    # rejected
    # completed
    # cancelled

    payment_status = db.Column(
        db.String(20),
        default="unpaid"
    )
    # unpaid
    # paid

    is_active = db.Column(
    db.Boolean,
    default=False
    )

    is_deleted = db.Column(
    db.Boolean,
    default=False
    )

    # =========================================
    # TIMESTAMPS
    # =========================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # =========================================
    # RELATIONSHIPS
    # =========================================

    work = db.relationship(
        "Work",
        backref="bookings",
        lazy=True
    )

    user = db.relationship(
    "User",
    foreign_keys=[user_id],
    backref="user_bookings"
    )

    owner = db.relationship(
    "User",
    foreign_keys=[owner_id],
    backref="owner_bookings"
    )

    # =========================================
    # STRING METHOD
    # =========================================

    def __repr__(self):

        return f"<Booking {self.id}>"
