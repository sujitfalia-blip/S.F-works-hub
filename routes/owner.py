from flask import Blueprint, render_template, session, redirect, request
from models.user import User
from models.work import Work
from extensions import db
from services.role_service import can_manage_booking
from extensions import socketio
from flask import jsonify, request, session
from sqlalchemy import func
from datetime import datetime, timedelta
from functools import wraps

owner = Blueprint('owner', __name__)


def is_owner():
    return session.get('role') == "owner"


def owner_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('role') != "owner":
            return "Unauthorized", 403
        return f(*args, **kwargs)
    return wrapper



# =================================================
# 👤 USER CONTROL
# =================================================

@owner.route('/owner/approve/<int:id>')
def approve(id):

    if not owner_only():
        return "Unauthorized"

    user = User.query.get(id)
    if not user:
        return "User not found"

    if user.role not in ["admin", "super_admin"]:
        return "No approval needed"

    user.status = "active"
    db.session.commit()

    return redirect('/owner/dashboard')

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

    # 🔁 transfer logic
    user.controller_id = controller.id
    db.session.commit()

    # 🔔 realtime notification
    socketio.emit("notify", {
        "message": f"{user.name} transferred successfully 🔁"
    })

    return redirect('/owner/dashboard')

# ================= WORK CONTROL =================

@owner.route('/owner/works')
@owner_only
def all_works():

    # 🔍 FILTER
    status = request.args.get("status")

    # ✅ BASE QUERY
    query = Work.query.filter_by(
        is_deleted=False
    )

    # ✅ STATUS FILTER
    if status:
        query = query.filter_by(status=status)

    # ✅ GET WORKS
    works = query.order_by(
        Work.id.desc()
    ).all()

    # ✅ RETURN PAGE
    return render_template(
        "owner_works.html",
        works=works
    )

@owner.route('/owner/work/approve/<int:id>')
def approve_work(id):

    if not owner_only():
        return "Unauthorized"

    work = Work.query.get(id)
    if not work:
        return "Not found"

    work.status = "approved"
    work.is_active = True
    work.approved_by = session.get('user_id')

    db.session.commit()
    return redirect('/owner/works')


@owner.route('/owner/work/reject/<int:id>')
def reject_work(id):

    if not owner_only():
        return "Unauthorized"

    work = Work.query.get(id)
    if not work:
        return "Not found"

    work.status = "rejected"
    work.is_active = False
    work.rejected_by = session.get('user_id')

    db.session.commit()
    return redirect('/owner/works')


@owner.route('/owner/work/edit/<int:id>', methods=['GET', 'POST'])
def edit_work(id):

    if not owner_only():
        return "Unauthorized"

    work = Work.query.get(id)
    if not work:
        return "Not found"

    if request.method == "GET":
        return render_template("edit_work.html", work=work)

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


@owner.route('/owner/work/delete/<int:id>')
def delete_work(id):

    if not owner_only():
        return "Unauthorized"

    work = Work.query.get(id)
    if not work:
        return "Not found"

    work.is_deleted = True
    work.status = "deleted"
    work.is_active = False

    db.session.commit()
    return redirect('/owner/works')  
    
@owner.route('/owner/analytics')
def owner_analytics():

    # 🔐 security
    if session.get("role") != "owner":
        return jsonify({"error": "Unauthorized"}), 403

    # 📅 dynamic range (default 30 days)
    days = request.args.get("days", 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)

    # ================= WORK STATS =================
    total_works = db.session.query(func.count(Work.id)).scalar()

    approved_works = db.session.query(func.count(Work.id))\
        .filter(Work.status == "approved").scalar()

    pending_works = db.session.query(func.count(Work.id))\
        .filter(Work.status == "pending").scalar()

    rejected_works = db.session.query(func.count(Work.id))\
        .filter(Work.status == "rejected").scalar()

    deleted_works = db.session.query(func.count(Work.id))\
        .filter(Work.is_deleted == True).scalar()

    # ================= USER STATS =================
    total_users = db.session.query(func.count(User.id))\
        .filter(User.role == "user").scalar()

    active_users = db.session.query(func.count(User.id))\
        .filter(User.role == "user", User.status == "active").scalar()

    blocked_users = total_users - active_users

    # ================= GROWTH (WORKS) =================
    work_growth = db.session.query(
        func.date(Work.created_at),
        func.count(Work.id)
    ).filter(
        Work.created_at >= start_date
    ).group_by(func.date(Work.created_at)).all()

    # ================= GROWTH (USERS) =================
    user_growth = db.session.query(
        func.date(User.created_at),
        func.count(User.id)
    ).filter(
        User.role == "user",
        User.created_at >= start_date
    ).group_by(func.date(User.created_at)).all()

    # ================= LAST 7 DAYS =================
    last_7 = datetime.utcnow() - timedelta(days=7)

    new_users_7d = db.session.query(func.count(User.id))\
        .filter(User.role == "user", User.created_at >= last_7).scalar()

    new_works_7d = db.session.query(func.count(Work.id))\
        .filter(Work.created_at >= last_7).scalar()

    # ================= RESPONSE =================
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
                    {"date": str(g[0]), "count": g[1]} for g in work_growth
                ],
                "users": [
                    {"date": str(g[0]), "count": g[1]} for g in user_growth
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
@role_required("owner")
def owner_dashboard():

    # ================= USERS =================
    total_users = User.query.filter_by(role="user").count()

    # ================= WORKS (SAFE FIX) =================
    total_works = Work.query.filter_by(is_deleted=False).count()

    # ================= EXTRA STATS =================
    active_works = Work.query.filter_by(status="active", is_deleted=False).count()

    return render_template(
        "owner/dashboard.html",
        total_users=total_users,
        total_works=total_works,
        active_works=active_works
    )
    
