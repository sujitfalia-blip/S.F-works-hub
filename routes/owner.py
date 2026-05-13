from flask import Blueprint, render_template, session, redirect, request, jsonify
from functools import wraps
from sqlalchemy import func
from datetime import datetime, timedelta

from extensions import db, socketio

from models.user import User
from models.work import Work

owner = Blueprint('owner', __name__)


# =================================================
# 🔐 ROLE REQUIRED DECORATOR
# =================================================
def role_required(role):

    def decorator(f):

        @wraps(f)
        def wrapper(*args, **kwargs):

            if session.get("role") != role:
                return "Unauthorized", 403

            return f(*args, **kwargs)

        return wrapper

    return decorator


# =================================================
# 🔐 OWNER ONLY
# =================================================
def owner_only(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if session.get("role") != "owner":
            return "Unauthorized", 403

        return f(*args, **kwargs)

    return wrapper


# =================================================
# 👤 APPROVE ADMIN / SUPER ADMIN
# =================================================
@owner.route('/owner/approve/<int:id>')
@owner_only
def approve(id):

    user = User.query.get(id)

    if not user:
        return "User not found"

    if user.role not in ["admin", "super_admin"]:
        return "No approval needed"

    user.status = "active"

    db.session.commit()

    return redirect('/owner/dashboard')


# =================================================
# 🔁 TRANSFER USER
# =================================================
@owner.route('/owner/transfer', methods=['POST'])
@owner_only
def transfer_user():

    user_id = int(request.form['user_id'])
    new_controller = int(request.form['new_controller'])

    # ❌ prevent same transfer
    if user_id == new_controller:
        return "Invalid operation"

    user = User.query.get(user_id)
    controller = User.query.get(new_controller)

    if not user or not controller:
        return "Invalid user"

    if controller.role not in ["admin", "super_admin"]:
        return "Invalid controller role"

    # 🔁 transfer
    user.controller_id = controller.id

    db.session.commit()

    # 🔔 realtime notify
    socketio.emit("notify", {
        "message": f"{user.name} transferred successfully 🔁"
    })

    return redirect('/owner/dashboard')


# =================================================
# 📋 ALL WORKS
# =================================================
@owner.route('/owner/works')
@owner_only
def all_works():

    status = request.args.get("status")

    query = Work.query.filter_by(
        is_deleted=False
    )

    if status:
        query = query.filter_by(status=status)

    works = query.order_by(
        Work.id.desc()
    ).all()

    return render_template(
        "owner_works.html",
        works=works
    )


# =================================================
# ✅ APPROVE WORK
# =================================================
@owner.route('/owner/work/approve/<int:id>')
@owner_only
def approve_work(id):

    work = Work.query.get(id)

    if not work:
        return "Not found"

    work.status = "approved"
    work.is_active = True
    work.approved_by = session.get('user_id')

    db.session.commit()

    return redirect('/owner/works')


# =================================================
# ❌ REJECT WORK
# =================================================
@owner.route('/owner/work/reject/<int:id>')
@owner_only
def reject_work(id):

    work = Work.query.get(id)

    if not work:
        return "Not found"

    work.status = "rejected"
    work.is_active = False
    work.rejected_by = session.get('user_id')

    db.session.commit()

    return redirect('/owner/works')


# =================================================
# ✏️ EDIT WORK
# =================================================
@owner.route('/owner/work/edit/<int:id>', methods=['GET', 'POST'])
@owner_only
def edit_work(id):

    work = Work.query.get(id)

    if not work:
        return "Not found"

    if request.method == "GET":

        return render_template(
            "edit_work.html",
            work=work
        )

    work.title = request.form['title']
    work.workers_needed = request.form['workers_needed']
    work.salary = request.form['salary']
    work.date = request.form['date']
    work.time = request.form['time']
    work.phone = request.form['phone']

    work.edit_count = (work.edit_count or 0) + 1
    work.edited_by = session.get('user_id')

    work.status = "pending"
    work.is_active = False

    db.session.commit()

    return redirect('/owner/works')


# =================================================
# 🗑 DELETE WORK
# =================================================
@owner.route('/owner/work/delete/<int:id>')
@owner_only
def delete_work(id):

    work = Work.query.get(id)

    if not work:
        return "Not found"

    work.is_deleted = True
    work.status = "deleted"
    work.is_active = False

    db.session.commit()

    return redirect('/owner/works')


# =================================================
# 📊 OWNER ANALYTICS API
# =================================================
@owner.route('/owner/analytics')
@owner_only
def owner_analytics():

    days = request.args.get("days", 30, type=int)

    start_date = datetime.utcnow() - timedelta(days=days)

    # ================= WORK STATS =================
    total_works = db.session.query(
        func.count(Work.id)
    ).scalar()

    approved_works = db.session.query(
        func.count(Work.id)
    ).filter(
        Work.status == "approved"
    ).scalar()

    pending_works = db.session.query(
        func.count(Work.id)
    ).filter(
        Work.status == "pending"
    ).scalar()

    rejected_works = db.session.query(
        func.count(Work.id)
    ).filter(
        Work.status == "rejected"
    ).scalar()

    deleted_works = db.session.query(
        func.count(Work.id)
    ).filter(
        Work.is_deleted == True
    ).scalar()

    # ================= USER STATS =================
    total_users = db.session.query(
        func.count(User.id)
    ).filter(
        User.role == "user"
    ).scalar()

    active_users = db.session.query(
        func.count(User.id)
    ).filter(
        User.role == "user",
        User.status == "active"
    ).scalar()

    blocked_users = total_users - active_users

    # ================= GROWTH =================
    work_growth = db.session.query(
        func.date(Work.created_at),
        func.count(Work.id)
    ).filter(
        Work.created_at >= start_date
    ).group_by(
        func.date(Work.created_at)
    ).all()

    user_growth = db.session.query(
        func.date(User.created_at),
        func.count(User.id)
    ).filter(
        User.role == "user",
        User.created_at >= start_date
    ).group_by(
        func.date(User.created_at)
    ).all()

    # ================= LAST 7 DAYS =================
    last_7 = datetime.utcnow() - timedelta(days=7)

    new_users_7d = db.session.query(
        func.count(User.id)
    ).filter(
        User.role == "user",
        User.created_at >= last_7
    ).scalar()

    new_works_7d = db.session.query(
        func.count(Work.id)
    ).filter(
        Work.created_at >= last_7
    ).scalar()

    return jsonify({

        "success": True,

        "data": {

            "works": {
                "total": total_works,
                "approved": approved_works,
                "pending": pending_works,
                "rejected": rejected_works,
                "deleted": deleted_works
            },

            "users": {
                "total": total_users,
                "active": active_users,
                "blocked": blocked_users,
                "new_last_7_days": new_users_7d
            },

            "growth": {

                "works": [
                    {
                        "date": str(g[0]),
                        "count": g[1]
                    }
                    for g in work_growth
                ],

                "users": [
                    {
                        "date": str(g[0]),
                        "count": g[1]
                    }
                    for g in user_growth
                ]
            },

            "recent": {
                "new_users_7d": new_users_7d,
                "new_works_7d": new_works_7d
            }
        }
    })


# =================================================
# 🏠 OWNER DASHBOARD
# =================================================
@owner.route('/owner/dashboard')
@owner_only
def owner_dashboard():

    # ================= USERS =================
    total_users = User.query.filter_by(
        role="user"
    ).count()

    # ================= ADMINS =================
    total_admins = User.query.filter(
        User.role.in_(["admin", "super_admin"])
    ).count()

    # ================= PENDING ADMINS =================
    pending_admins = User.query.filter(
        User.role.in_(["admin", "super_admin"]),
        User.status == "pending"
    ).all()

    # ================= WORKS =================
    total_works = Work.query.filter_by(
        is_deleted=False
    ).count()

    approved_works = Work.query.filter_by(
        status="approved",
        is_deleted=False
    ).count()

    pending_works = Work.query.filter_by(
        status="pending",
        is_deleted=False
    ).count()

# ================= ALL USERS =================
latest_users = User.query.order_by(
    User.id.desc()
).all()


# ================= LATEST BOOKINGS =================
from models.booking import Booking

latest_bookings = Booking.query.order_by(
    Booking.id.desc()
).limit(20).all()


return render_template(
    "owner/dashboard.html",

    total_users=total_users,
    total_admins=total_admins,

    total_works=total_works,
    approved_works=approved_works,
    pending_works=pending_works,

    pending_admins=pending_admins,

    latest_users=latest_users,
    latest_bookings=latest_bookings
)
