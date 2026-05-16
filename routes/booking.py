# =========================================
# routes/booking.py
# PRODUCTION VERSION
# =========================================

from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    abort,
    flash,
    request
)

from sqlalchemy import desc

from extensions import db

from models.booking import Booking
from models.user import User
from models.work_model import Work

from permissions import (
    is_admin,
    is_super_admin,
    is_owner,
    can_manage_booking
)

booking = Blueprint(
    "booking",
    __name__
)


# =========================================
# LOGIN CHECK
# =========================================

def login_required():

    if not session.get("user_id"):
        return False

    return True


# =========================================
# USER BOOKINGS
# USER CAN SEE OWN BOOKINGS
# =========================================

@booking.route("/my-bookings")
def my_bookings():

    if not login_required():
        return redirect("/auth/login")

    bookings = Booking.query.filter_by(
        user_id=session.get("user_id"),
        is_deleted=False
    ).order_by(
        desc(Booking.id)
    ).all()

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )

# =========================================
# USER CREATE BOOKING
# =========================================
@booking.route("/create_booking/<int:owner_id>", methods=["POST"])
def create_booking(owner_id):

    # ✅ login check (correct way)
    if "user_id" not in session:
        flash("Login required", "danger")
        return redirect("/auth/login")

    user_id = session.get("user_id")

    # =====================================
    # FIND WORK
    # =====================================

    work = Work.query.get_or_404(owner_id)

    # =====================================
    # OWNER ID
    # =====================================

    owner_id = work.user_id

    # =====================================
    # PREVENT SELF BOOKING
    # =====================================

    if owner_id == user_id:

        flash(
            "You cannot book your own work",
            "warning"
        )

        return redirect(request.referrer or "/")

    # =====================================
    # CHECK EXISTING BOOKING
    # =====================================

    existing = Booking.query.filter_by(
        user_id=user_id,
        owner_id=owner_id,
        is_deleted=False
    ).first()

    if existing:

        flash(
            "Already booked",
            "info"
        )

        return redirect(request.referrer or "/")

    # =====================================
    # CREATE BOOKING
    # =====================================

    booking_data = Booking(
        user_id=user_id,
        owner_id=owner_id,
        status="pending",
        is_active=False
    )

    db.session.add(booking_data)

    db.session.commit()

    flash(
        "Booking created successfully",
        "success"
    )

    return redirect("/my-bookings")


# =========================================
# ADMIN BOOKINGS
# ADMIN CAN SEE OWN USERS BOOKINGS
# =========================================

@booking.route("/bookings")
def admin_bookings():

    if not login_required():
        return redirect("/auth/login")

    # =====================================
    # OWNER FULL ACCESS
    # =====================================

    if is_owner():

        bookings = Booking.query.filter_by(
            is_deleted=False
        ).order_by(
            desc(Booking.id)
        ).all()

        return render_template(
            "bookings.html",
            bookings=bookings
        )

    # =====================================
    # SUPER ADMIN
    # =====================================

    if is_super_admin():

        admins = User.query.filter_by(
            role="admin",
            created_by=session.get("user_id"),
            is_deleted=False
        ).all()

        admin_ids = [a.id for a in admins]

        users = User.query.filter(
            User.created_by.in_(admin_ids),
            User.role == "user",
            User.is_deleted == False
        ).all()

        user_ids = [u.id for u in users]

        bookings = Booking.query.filter(
            Booking.user_id.in_(user_ids),
            Booking.is_deleted == False
        ).order_by(
            desc(Booking.id)
        ).all()

        return render_template(
            "bookings.html",
            bookings=bookings
        )

    # =====================================
    # ADMIN
    # =====================================

    if is_admin():

        users = User.query.filter_by(
            created_by=session.get("user_id"),
            role="user",
            is_deleted=False
        ).all()

        user_ids = [u.id for u in users]

        bookings = Booking.query.filter(
            Booking.user_id.in_(user_ids),
            Booking.is_deleted == False
        ).order_by(
            desc(Booking.id)
        ).all()

        return render_template(
            "bookings.html",
            bookings=bookings
        )

    # =====================================
    # NORMAL USER NOT ALLOWED
    # =====================================

    abort(403)


# =========================================
# APPROVE BOOKING
# =========================================

@booking.route(
    "/booking/approve/<int:id>",
    methods=["POST"]
)
def approve_booking(id):

    if not login_required():
        return redirect("/auth/login")

    booking_data = db.session.get(
        Booking,
        id
    )

    if not booking_data:
        abort(404)

    if not can_manage_booking(booking_data):
        abort(403)

    booking_data.status = "approved"

    booking_data.is_active = True

    booking_data.approved_by = session.get(
        "user_id"
    )

    db.session.commit()

    flash(
        "Booking approved successfully",
        "success"
    )

    return redirect(request.referrer or "/bookings")


# =========================================
# REJECT BOOKING
# =========================================

@booking.route(
    "/booking/reject/<int:id>",
    methods=["POST"]
)
def reject_booking(id):

    if not login_required():
        return redirect("/auth/login")

    booking_data = db.session.get(
        Booking,
        id
    )

    if not booking_data:
        abort(404)

    if not can_manage_booking(booking_data):
        abort(403)

    booking_data.status = "rejected"

    booking_data.is_active = False

    booking_data.rejected_by = session.get(
        "user_id"
    )

    db.session.commit()

    flash(
        "Booking rejected successfully",
        "warning"
    )

    return redirect(request.referrer or "/bookings")


# =========================================
# BLOCK BOOKING
# =========================================

@booking.route(
    "/booking/block/<int:id>",
    methods=["POST"]
)
def block_booking(id):

    if not login_required():
        return redirect("/auth/login")

    booking_data = db.session.get(
        Booking,
        id
    )

    if not booking_data:
        abort(404)

    if not can_manage_booking(booking_data):
        abort(403)

    booking_data.status = "blocked"

    booking_data.is_active = False

    booking_data.blocked_by = session.get(
        "user_id"
    )

    db.session.commit()

    flash(
        "Booking blocked successfully",
        "danger"
    )

    return redirect(request.referrer or "/bookings")


# =========================================
# UNBLOCK BOOKING
# =========================================

@booking.route(
    "/booking/unblock/<int:id>",
    methods=["POST"]
)
def unblock_booking(id):

    if not login_required():
        return redirect("/auth/login")

    booking_data = db.session.get(
        Booking,
        id
    )

    if not booking_data:
        abort(404)

    if not can_manage_booking(booking_data):
        abort(403)

    booking_data.status = "pending"

    booking_data.is_active = False

    db.session.commit()

    flash(
        "Booking unblocked successfully",
        "success"
    )

    return redirect(request.referrer or "/bookings")


# =========================================
# DELETE BOOKING
# =========================================

@booking.route(
    "/booking/delete/<int:id>",
    methods=["POST"]
)
def delete_booking(id):

    if not login_required():
        return redirect("/auth/login")

    booking_data = db.session.get(
        Booking,
        id
    )

    if not booking_data:
        abort(404)

    if not can_manage_booking(booking_data):
        abort(403)

    booking_data.status = "deleted"

    booking_data.is_deleted = True

    booking_data.deleted_by = session.get(
        "user_id"
    )

    db.session.commit()

    flash(
        "Booking deleted successfully",
        "danger"
    )

    return redirect(request.referrer or "/bookings")
