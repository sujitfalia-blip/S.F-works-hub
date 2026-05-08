from flask import Blueprint, request, session, redirect
from services.create_work_service import create_work

work = Blueprint("work", __name__)

@work.route('/create', methods=['POST'])
def create_work_route():

    # ================= LOGIN CHECK =================
    if 'user_id' not in session:
        return redirect('/login')

    # ================= DATA =================
    data = {
        "title": request.form.get("title"),
        "workers": request.form.get("workers"),
        "salary": request.form.get("salary"),
        "date": request.form.get("date"),
        "time": request.form.get("time"),
        "phone": request.form.get("phone"),
        "user_id": session.get("user_id")
    }

    # ================= SERVICE CALL =================
    result = create_work(data)

    if not result:
        return "error", 500

    return "success"
    
