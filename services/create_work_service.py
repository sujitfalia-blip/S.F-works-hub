from models.work import Work
from extensions import db, socketio


def create_work(data):

    try:
        # ================= CREATE WORK =================
        work = Work(
            title=data.get("title"),
            workers_needed=int(data.get("workers") or 0),
            salary=int(data.get("salary") or 0),
            date=data.get("date"),
            time=data.get("time"),
            phone=data.get("phone"),
            created_by=data.get("user_id")
        )

        # ================= SAVE =================
        db.session.add(work)
        db.session.commit()

        # ================= LIVE UPDATE =================
        socketio.emit(
            "new_work",
            {
                "id": work.id,
                "title": work.title
            },
            to=None
        )

        return work

    except Exception as e:
        db.session.rollback()
        print("Create Work Error:", e)
        return None
        
