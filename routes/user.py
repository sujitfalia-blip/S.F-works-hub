from flask import (
    Blueprint,
    request,
    session,
    redirect,
    render_template,
    flash
)

from models.work_model import Work
from models.work_application_model import WorkApplication
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
@user.route('/post_work', methods=['GET', 'POST'])
def post_work():

    # 🔐 LOGIN CHECK
    if 'user_id' not in session:
        return redirect('/auth/login')

    # ================= GET REQUEST =================
    if request.method == "GET":
        return render_template("create_work.html")

    # ================= POST REQUEST =================
    title = request.form.get('title')
    workers = request.form.get('workers')
    salary = request.form.get('salary')
    date = request.form.get('date')
    time = request.form.get('time')
    phone = request.form.get('phone')

    # 🔴 VALIDATION
    if not all([title, workers, salary, date, time, phone]):
    flash("সব ফিল্ড পূরণ করা আবশ্যক!")
    return redirect('/user/post_work')

    if len(phone) < 10:
    flash("সঠিক মোবাইল নম্বর দিন!")
    return redirect('/user/post_work')
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

    # =================================================
    # 🔐 SESSION CHECK
    # =================================================
    user_id = session.get("user_id")

    if not user_id:
        return redirect('/auth/login')

    # =================================================
    # 👤 CURRENT USER
    # =================================================
    current_user_data = db.session.get(User, user_id)

    if not current_user_data:
        session.clear()
        return redirect('/auth/login')

    # =================================================
    # 💼 ALL APPROVED WORKS
    # =================================================
    works = (
        db.session.query(Work, User)
        .join(
            User,
            Work.user_id == User.id
        )
        .filter(
            Work.status == "approved"
        )
        .order_by(
            Work.created_at.desc()
        )
        .all()
    )

    # =================================================
    # 👥 ALL USER PROFILES
    # =================================================
    profiles = (
        Profile.query
        .join(
            User,
            Profile.user_id == User.id
        )
        .filter(
            Profile.user_id != user_id
        )
        .order_by(
            Profile.id.desc()
        )
        .all()
    )

    # =================================================
    # 📊 DASHBOARD STATS
    # =================================================
    total_works = Work.query.filter_by(
        status="approved"
    ).count()

    total_profiles = Profile.query.count()

    # =================================================
    # 🖥️ RENDER TEMPLATE
    # =================================================
    return render_template(

        "user/dashboard.html",

        # CURRENT USER
        current_user=current_user_data,

        # WORKS
        works=works,
        total_works=total_works,

        # PROFILES
        profiles=profiles,
        total_profiles=total_profiles
    )

@user.route('/apply_work/<int:work_id>', methods=['POST'])
@role_required("user")
def apply_work(work_id):

    # ================= USER CHECK =================
    user_id = session.get("user_id")

    if not user_id:
        return redirect('/auth/login')

    try:

        # ================= CHECK WORK =================
        work = Work.query.filter_by(
            id=work_id,
            status="approved"
        ).first()

        if not work:
            flash("Work not found!")
            return redirect('/user/dashboard')

        # ================= BLOCK OWN APPLY =================
        if work.user_id == user_id:
            flash("You cannot apply to your own work!")
            return redirect('/user/dashboard')

        # ================= DUPLICATE CHECK =================
        already_applied = WorkApplication.query.filter_by(
            user_id=user_id,
            work_id=work_id
        ).first()

        if already_applied:
            flash("You already applied!")
            return redirect('/user/dashboard')

        # ================= CREATE APPLICATION =================
        application = WorkApplication(
            user_id=user_id,
            work_id=work_id,
            status="pending"
        )

        # ================= SAVE =================
        db.session.add(application)
        db.session.commit()

        flash("Application submitted successfully!")

    except Exception as e:

        db.session.rollback()

        print("Apply Work Error:", str(e))

        flash("Something went wrong!")

    # ================= REDIRECT =================
    return redirect('/user/dashboard')
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
