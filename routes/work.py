from flask import Blueprint, request, session, redirect
from services.create_work_service import create_work

work = Blueprint("work", __name__)

@work.route('/create', methods=['POST'])
def create_work():

    if 'user_id' not in session:
        return redirect('/login')

    data = {
        "title": request.form.get("title"),
        "workers": request.form.get("workers"),
        "salary": request.form.get("salary"),
        "date": request.form.get("date"),
        "time": request.form.get("time"),
        "phone": request.form.get("phone")
    }

    create_work(data)

    return "success"
    
