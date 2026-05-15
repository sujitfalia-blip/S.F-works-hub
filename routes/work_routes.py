from flask import (
    Blueprint,
    request,
    session,
    redirect,
    render_template,
    flash,
    url_for
)

from extensions import db
from models.work_model import Work
from models.work_application_model import WorkApplication
from services.create_work_service import create_work as create_work_service

work = Blueprint("work", __name__)


# =====================================================
# CREATE WORK
# =====================================================
@work.route('/create', methods=['GET', 'POST'])
def create_work_route():

    # LOGIN CHECK
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # SHOW PAGE
    if request.method == 'GET':
        return render_template("create_work.html")

    # FORM DATA
    data = {
        "title": request.form.get("title"),
        "description": request.form.get("description"),
        "workers": request.form.get("workers"),
        "salary": request.form.get("salary"),
        "date": request.form.get("date"),
        "time": request.form.get("time"),
        "phone": request.form.get("phone")
    }

    # VALIDATION
    if not data["title"] or not data["salary"]:
        flash("Title and Salary required")
        return redirect(url_for('work.create_work_route'))

    try:
        result = create_work_service(data, session["user_id"])

        if not result:
            flash("Failed to create work")
            return redirect(url_for('work.create_work_route'))

        flash("Work posted successfully")
        return redirect(url_for('work.work_list'))

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}")
        return redirect(url_for('work.create_work_route'))


# =====================================================
# ALL WORK LIST
# =====================================================
@work.route('/works')
def work_list():

    works = Work.query.filter_by(
        status="active",
        is_deleted=False
    ).order_by(
        Work.id.desc()
    ).all()

    return render_template("work_list.html", works=works)


# =====================================================
# APPLY WORK
# =====================================================
@work.route('/apply_work/<int:id>', methods=['POST'])
def apply_work(id):

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    work_item = Work.query.filter_by(
        id=id,
        status="active",
        is_deleted=False
    ).first()

    if not work_item:
        flash("Work not found")
        return redirect(url_for('work.work_list'))

    # DUPLICATE CHECK
    already_applied = WorkApplication.query.filter_by(
        user_id=session['user_id'],
        work_id=id
    ).first()

    if already_applied:
        flash("Already applied")
        return redirect(url_for('work.work_list'))

    try:
        application = WorkApplication(
            user_id=session['user_id'],
            work_id=id
        )

        db.session.add(application)
        db.session.commit()

        flash("Applied successfully")
        return redirect(url_for('work.work_list'))

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}")
        return redirect(url_for('work.work_list'))
