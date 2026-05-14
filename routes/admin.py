from flask import Blueprint, render_template, session, jsonify, request
from functools import wraps
from models.user import User
from models.booking import Booking
from models.work_model import Work
from extensions import db
from sqlalchemy.orm import load_only

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ================= RESPONSE =================

def success(data=None, message="OK"):
    return jsonify({"success": True, "message": message, "data": data}), 200

def error(msg="Error", code=400):
    return jsonify({"success": False, "message": msg}), code


# ================= AUTH =================

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            return error("Unauthorized", 403)
        return f(*args, **kwargs)
    return wrapper


# ================= DASHBOARD =================

@admin_bp.route("/")
@admin_required
def dashboard():

    user_id = session.get("user_id")

    total = User.query.filter_by(controller_id=user_id).count()
    active = User.query.filter_by(controller_id=user_id, status="active").count()
    blocked = User.query.filter_by(controller_id=user_id, status="blocked").count()

    return render_template(
        "admin/dashboard.html",
        total=total,
        active=active,
        blocked=blocked,
        user_id=user_id
    )


# ================= USERS =================

@admin_bp.route("/users")
@admin_required
def users():

    user_id = session.get("user_id")

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("limit", 20, type=int)
    search = request.args.get("search", "")

    query = User.query.filter_by(controller_id=user_id)\
        .options(load_only(User.id, User.name, User.status))

    if search:
        query = query.filter(User.name.ilike(f"%{search}%"))

    users = query.paginate(page=page, per_page=per_page)

    return success({
        "users": [{
            "id": u.id,
            "name": u.name,
            "status": u.status
        } for u in users.items],
        "pagination": {
            "total": users.total,
            "pages": users.pages,
            "current": users.page
        }
    })


# ================= USER STATUS =================

@admin_bp.route("/user/<int:id>/status", methods=["POST"])
@admin_required
def update_user_status(id):

    user = User.query.get_or_404(id)

    if user.controller_id != session.get("user_id"):
        return error("Unauthorized", 403)

    data = request.get_json(silent=True) or {}
    status = data.get("status")

    if status not in ["active", "blocked"]:
        return error("Invalid status")

    user.status = status
    db.session.commit()

    return success(message=f"User {status}")


# ================= BULK ACTION =================

@admin_bp.route("/users/bulk", methods=["POST"])
@admin_required
def bulk_users():

    data = request.get_json(silent=True) or {}
    ids = data.get("ids", [])
    action = data.get("action")

    if action not in ["block", "unblock"]:
        return error("Invalid action")

    users = User.query.filter(
        User.id.in_(ids),
        User.controller_id == session.get("user_id")
    ).all()

    for u in users:
        u.status = "blocked" if action == "block" else "active"

    db.session.commit()

    return success(message="Bulk action completed")


# ================= ANALYTICS =================

@admin_bp.route("/analytics")
@admin_required
def analytics():

    user_id = session.get("user_id")

    total = User.query.filter_by(controller_id=user_id).count()
    active = User.query.filter_by(controller_id=user_id, status="active").count()
    blocked = User.query.filter_by(controller_id=user_id, status="blocked").count()

    bookings = Booking.query.join(User)\
        .filter(User.controller_id == user_id).count()

    works = Work.query.filter_by(created_by=user_id).count()

    return success({
        "users": {
            "total": total,
            "active": active,
            "blocked": blocked
        },
        "bookings": bookings,
        "works": works
    })
