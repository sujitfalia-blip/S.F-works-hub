from flask import Blueprint, session, redirect, render_template
from models.booking import Booking
from extensions import db

booking = Blueprint('booking', __name__)


def can_manage_booking():
    return session.get("role") == "admin"


@booking.route('/bookings')
def all_bookings():

    if not can_manage_booking():
        return "Unauthorized"

    data = Booking.query.filter_by(
        is_deleted=False
    ).order_by(
        Booking.id.desc()
    ).all()

    return render_template(
        "bookings.html",
        bookings=data
    )


@booking.route('/booking/approve/<int:id>', methods=['POST'])
def approve(id):

    if not can_manage_booking():
        return "Unauthorized"

    b = db.session.get(Booking, id)

    if not b:
        return "Not found"

    b.status = "approved"
    b.is_active = True
    b.approved_by = session.get('user_id')

    db.session.commit()

    return redirect('/bookings')
