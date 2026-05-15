from flask import (
    Blueprint,
    request,
    session,
    redirect,
    render_template,
    flash
)

from models.work_model import Work
from models.user import User
from models.profile import Profile
from models.chat import Chat

from extensions import db
from services.otp_service import generate_otp
from decorators.auth import role_required


user = Blueprint("user", __name__, url_prefix="/user")


# =================================================
# 🟡 WORK POST (OTP + PENDING SYSTEM)
# =================================================
@user.route('/post_work', methods=['POST'])
def post_work():

    # 🔐 LOGIN CHECK
    if 'user_id' not in session:
        return redirect('/auth/login')

    title = request.form.get('title')
    workers = request.form.get('workers')
    salary = request.form.get('salary')
    date = request.form.get('date')
    time = request.form.get('time')
    phone = request.form.get('phone')

    # 🔴 VALIDATION
    if not all([title, workers, salary, date, time, phone]):
        flash("সব ফিল্ড পূরণ করা আবশ্যক!")
        return redirect('/user/dashboard')

    if len(phone) < 10:
        flash("সঠিক মোবাইল নম্বর দিন!")
        return redirect('/user/dashboard')

    # 📱 OTP GENERATE (future verification)
    otp = generate_otp(phone)
    print("OTP:", otp)

    # 🧠 SAVE TO DATABASE (PENDING)
    work = Work(
        title=title,
        description=f"{workers} workers needed | Salary: {salary} | Date: {date} | Time: {time}",
        mobile=phone,
        user_id=session['user_id'],
        status="pending"
    )

    db.session.add(work)
    db.session.commit()

    flash("Work submitted for approval!")
    return redirect('/user/dashboard')


# =================================================
# 🟢 USER DASHBOARD (ONLY APPROVED WORK)
# =================================================
@user.route('/dashboard')
@role_required("user")
def dashboard():

    if 'user_id' not in session:
        return redirect('/auth/login')

    user_id = session['user_id']

    works = Work.query.filter_by(
        user_id=user_id,
        status="approved"
    ).order_by(Work.id.desc()).all()

    current_user_data = User.query.get(user_id)

    profiles = (
        Profile.query
        .join(User)
        .filter(Profile.user_id != user_id)
        .all()
    )

    return render_template(
        "user/dashboard.html",
        works=works,
        profiles=profiles,
        current_user=current_user_data
    )


# =================================================
# 💬 CHAT SYSTEM (UNCHANGED BUT CLEAN)
# =================================================
@user.route("/chat/<int:user_id>")
def chat(user_id):

    if 'user_id' not in session:
        return redirect("/auth/login")

    current_user_id = session['user_id']

    # ❌ SELF CHAT BLOCK
    if current_user_id == user_id:
        return redirect("/user/dashboard")

    receiver = User.query.get_or_404(user_id)

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
