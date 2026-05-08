from models.work import Work
from extensions import db, socketio


# ================= VALIDATION =================
def validate_work_data(data):
    if not data.get("title"):
        return "Title required"

    if not data.get("workers"):
        return "Workers required"

    if not data.get("salary"):
        return "Salary required"

    return None


# ================= CREATE WORK =================
def create_work(data):

    try:
        # ================= VALIDATE =================
        error = validate_work_data(data)
        if error:
            print("Validation Error:", error)
            return None

        # ================= SAFE CONVERT =================
        workers = int(data.get("workers") or 0)
        salary = int(data.get("salary") or 0)

        # ================= CREATE OBJECT =================
        work = Work(
            title=data.get("title"),
            workers_needed=workers,
            salary=salary,
            date=data.get("date"),
            time=data.get("time"),
            phone=data.get("phone"),
            created_by=data.get("user_id")
        )

        # ================= SAVE =================
        db.session.add(work)
        db.session.commit()

        # ================= SOCKET UPDATE =================
        socketio.emit(
            "new_work",
            {
                "id": work.id,
                "title": work.title
            }
        )

        return work

    except Exception as e:
        db.session.rollback()
        print("Create Work Error:", e)
        return None
        
