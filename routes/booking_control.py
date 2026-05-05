from flask import Blueprint, request, session, redirect, render_template
from models.booking import Booking
from extensions import db

booking = Blueprint('booking', __name__)


# ================= VIEW =================
@booking.route('/bookings')
def all_bookings():

    if not can_manage_booking():
        return "Unauthorized"

    data = Booking.query.filter_by(is_deleted=False)\
        .order_by(Booking.id.desc()).all()

    return render_template("bookings.html", bookings=data)


# ================= APPROVE =================
@booking.route('/booking/approve/<int:id>', methods=['POST'])
def approve(id):

    if not can_manage_booking():
        return "Unauthorized"

    b = Booking.query.get(id)
    if not b:
        return "Not found"

    b.status = "approved"
    b.is_active = True
    b.approved_by = session['user_id']

    db.session.commit()
    return redirect('/bookings')


# ================= REJECT =================
@booking.route('/booking/reject/<int:id>', methods=['POST'])
def reject(id):

    if not can_manage_booking():
        return "Unauthorized"

    b = Booking.query.get(id)
    if not b:
        return "Not found"

    b.status = "rejected"
    b.is_active = False
    b.rejected_by = session['user_id']

    db.session.commit()
    return redirect('/bookings')


# ================= BLOCK =================
@booking.route('/booking/block/<int:id>', methods=['POST'])
def block(id):

    if not can_manage_booking():
        return "Unauthorized"

    b = Booking.query.get(id)
    if not b:
        return "Not found"

    b.status = "blocked"
    b.is_active = False
    b.blocked_by = session['user_id']

    db.session.commit()
    return redirect('/bookings')


# ================= UNBLOCK =================
@booking.route('/booking/unblock/<int:id>', methods=['POST'])
def unblock(id):

    if not can_manage_booking():
        return "Unauthorized"

    b = Booking.query.get(id)
    if not b:
        return "Not found"

    b.status = "pending"
    b.is_active = True

    db.session.commit()
    return redirect('/bookings')


# ================= DELETE (SOFT) =================
@booking.route('/booking/delete/<int:id>', methods=['POST'])
def delete(id):

    if not can_manage_booking():
        return "Unauthorized"

    b = Booking.query.get(id)
    if not b:
        return "Not found"

    b.status = "deleted"
    b.is_deleted = True
    b.is_active = False
    b.deleted_by = session['user_id']

    db.session.commit()
    return redirect('/bookings')
