from flask import Blueprint, request, redirect, session, render_template, url_for
from functools import wraps

from models.user import User
from models.profile import Profile

from extensions import db

from werkzeug.security import generate_password_hash, check_password_hash

from services.referral_service import assign_control


auth = Blueprint('auth', __name__)


# =========================================================
# LOGIN REQUIRED
# =========================================================
def login_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)

    return wrapper


# =========================================================
# SIGNUP
# =========================================================
@auth.route('/signup', methods=['GET', 'POST'])
def signup():

    # ================= SHOW PAGE =================
    if request.method == 'GET':
        return render_template('signup.html')

    # ================= FORM DATA =================
    name = request.form.get('name')
    phone = request.form.get('phone')
    password_raw = request.form.get('password')
    role = request.form.get('role')

    # ================= ROLE FIX =================
    if role not in ["user", "admin", "super_admin"]:
        role = "user"

    # ================= VALIDATION =================
    if not all([name, phone, password_raw]):
        return "All fields required"

    # ================= PHONE CHECK =================
    existing = User.query.filter_by(phone=phone).first()

    if existing:
        return "Phone already registered"

    # ================= PASSWORD HASH =================
    password = generate_password_hash(password_raw)

    # ================= REFERRAL =================
    ref_id = request.form.get('ref_id')

    referrer = None

    if ref_id:
        referrer = User.query.get(ref_id)

    # ================= STATUS LOGIC =================
    # user = active
    # admin/super_admin = pending

    if role == "user":
        status = "active"
    else:
        status = "pending"

    # ================= CREATE USER =================
    user = User(
        name=name,
        phone=phone,
        password=password,
        role=role,
        status=status
    )

    # ================= ASSIGN CONTROL =================
    assign_control(user, referrer)

    try:

        # SAVE USER
        db.session.add(user)

        db.session.flush()

        # ================= CREATE PROFILE =================
        profile = Profile(
            user_id=user.id,
            name=name
        )

        db.session.add(profile)

        # ================= COMMIT =================
        db.session.commit()

    except Exception as e:

        db.session.rollback()

        return f"Signup error: {e}"

    # ================= MESSAGE =================
    if user.status == "pending":
        return "Signup successful. Wait for approval."

    return redirect(url_for('auth.login'))


# =========================================================
# LOGIN
# =========================================================
@auth.route('/login', methods=['GET', 'POST'])
def login():

    # ================= SHOW PAGE =================
    if request.method == 'GET':
        return render_template('login.html')

    # ================= FORM DATA =================
    phone = request.form.get('phone')
    password = request.form.get('password')

    # ================= VALIDATION =================
    if not phone or not password:
        return "All fields required"

    # ================= FIND USER =================
    user = User.query.filter_by(phone=phone).first()

    if not user:
        return "User not found"

    # ================= BLOCKED =================
    if user.status == "blocked":
        return "Account blocked"

    # ================= PENDING =================
    if user.status != "active":
        return "Account not approved yet"

    # ================= PASSWORD CHECK =================
    if not check_password_hash(user.password, password):
        return "Wrong password"

    # ================= SESSION =================
    session['user_id'] = user.id
    session['role'] = user.role

    # ================= REDIRECT =================
    if user.role == "owner":
        return redirect('/owner/dashboard')

    elif user.role == "super_admin":
        return redirect('/super/admins')

    elif user.role == "admin":
        return redirect('/admin/users')

    else:
        return redirect('/user/dashboard')


# =========================================================
# LOGOUT
# =========================================================
@auth.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('auth.login'))
