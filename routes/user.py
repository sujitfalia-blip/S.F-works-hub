from flask import (
    Blueprint,
    request,
    session,
    redirect,
    render_template,
    flash,
    url_for
)

from flask_login import login_required, current_user

from models.booking import Booking
from models.work_model import Work
from models.work_application_model import WorkApplication
from models.user import User
from models.profile import Profile
from models.chat import Chat

from extensions import db

from services.otp_service import generate_otp

from decorators.auth import role_required


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


# ================= CHAT PAGE =================
@user.route("/chat/<int:user_id>")
def chat(user_id):

    # ================= LOGIN CHECK =================
    if 'user_id' not in session:
        return redirect("/auth/login")

    current_user_id = session['user_id']

    # ================= SELF CHAT BLOCK =================
    if current_user_id == user_id:
        return redirect("/user/dashboard")

    # ================= RECEIVER =================
    receiver = User.query.get_or_404(user_id)

    # ================= MESSAGES LOAD =================
    messages = Chat.query.filter(
        (
            (Chat.sender_id == current_user_id) &
            (Chat.receiver_id == user_id)
        ) |
        (
            (Chat.sender_id == user_id) &
            (Chat.receiver_id == current_user_id)
        )
    ).order_by(Chat.created_at.asc()).all()

    return render_template(
        "chat.html",
        receiver=receiver,
        messages=messages,
        current_user_id=current_user_id
    )
# ================= USER DASHBOARD =================

@user.route('/dashboard')
@role_required("user")
def dashboard():

    # ================= LOGIN CHECK =================

    if 'user_id' not in session:
        return redirect('/auth/login')

    current_user_id = session['user_id']

    # ================= CURRENT USER =================

    current_user_data = User.query.get(current_user_id)

    # ================= OTHER USERS =================

    profiles = (
        Profile.query
        .join(User)
        .filter(Profile.user_id != current_user_id)
        .all()
    )

    # ================= RENDER =================

    return render_template(
        "user/dashboard.html",
        profiles=profiles,
        current_user=current_user_data
    )
