from flask import Blueprint
from functools import wraps
from flask import session, redirect

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return wrapper
    from flask import Blueprint, request, redirect, session
from models.user import User
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

# 🔗 referral logic
from services.referral_service import assign_control

auth = Blueprint('auth', __name__)


# ================= SIGNUP =================
from flask import Blueprint, request, redirect, render_template
from models.user import User
from models.profile import Profile
from extensions import db
from werkzeug.security import generate_password_hash

from services.referral_service import assign_control

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():

    # ================= SHOW PAGE =================
    if request.method == 'GET':
        return render_template('signup.html')

    # ================= HANDLE FORM =================
    name = request.form.get('name')
    phone = request.form.get('phone')
    password_raw = request.form.get('password')

    if not name or not phone or not password_raw:
        return "All fields required"

    # duplicate check
    if User.query.filter_by(phone=phone).first():
        return "Phone already registered"

    password = generate_password_hash(password_raw)

    # referral
    ref_id = request.form.get('ref_id')
    referrer = User.query.get(ref_id) if ref_id else None

    # create user
    user = User(
        phone=phone,
        password=password,
        role="user"
    )

    assign_control(user, referrer)

    try:
        db.session.add(user)
        db.session.flush()   # 🔥 get user.id before commit

        # profile auto create
        profile = Profile(
            user_id=user.id,
            name=name
        )
        db.session.add(profile)

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return "Signup error"

    return redirect('/login')


# ================= LOGIN =================
@auth.route('/login', methods=['GET', 'POST'])
def login():

    # 👉 GET → page show
    if request.method == 'GET':
        return render_template('login.html')
        
    phone = request.form.get('phone')
    password = request.form.get('password')

    if not phone or not password:
        return "All fields required"

    user = User.query.filter_by(phone=phone).first()

    if not user:
        return "User not found"

    # 🔒 blocked check
    if user.status == "blocked":
        return "Account blocked"

    # 🔴 approval check
    if user.status != "active":
        return "Account not approved yet"

    # 🔑 password check
    if not check_password_hash(user.password, password):
        return "Wrong password"

    # 🔐 session
    session['user_id'] = user.id
    session['role'] = user.role

    # 🔁 redirect
    if user.role == "owner":
        return redirect('/owner/dashboard')

    elif user.role == "super_admin":
        return redirect('/super/admins')

    elif user.role == "admin":
        return redirect('/admin/users')

    else:
        return redirect('/user/dashboard')


# ================= LOGOUT =================
@auth.route('/logout')
def logout():
    session.clear()
    return redirect('/')
  
