from flask import Blueprint, request, session, redirect, render_template

from models.work import Work
from extensions import db

from services.otp_service import generate_otp

from decorators.auth import role_required

from models.user import User

from models.profile import Profile

user = Blueprint("user", __name__, url_prefix="/user")


# ================= POST WORK =================
@user.route('/post_work', methods=['POST'])
def post_work():

    # 🔐 login check
    if 'user_id' not in session:
        return redirect('/login')

    title = request.form.get('title')
    workers = request.form.get('workers')
    salary = request.form.get('salary')
    date = request.form.get('date')
    time = request.form.get('time')
    phone = request.form.get('phone')

    # 🔴 validation
    if not all([title, workers, salary, date, time, phone]):
        return "All fields required"

    # 📱 OTP generate
    otp = generate_otp(phone)

    print("OTP:", otp)

    # 🧠 temp store
    session['work_data'] = {
        "title": title,
        "workers": workers,
        "salary": salary,
        "date": date,
        "time": time,
        "phone": phone
    }

    return "OTP Sent (check console)"


# ================= USER DASHBOARD =================
@user.route('/dashboard')
@role_required("user")
def dashboard():

    # login check
    if 'user_id' not in session:
        return redirect('/auth/login')

    current_user_id = session['user_id']

    # নিজের ছাড়া সব profile
    profiles = (
        Profile.query
        .join(User)
        .filter(Profile.user_id != current_user_id)
        .all()
    )

    return render_template(
        "user/dashboard.html",
        profiles=profiles
    )
    
