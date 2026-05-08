from models.work import Work
from extensions import db, socketio


def create_work(data):

    try:
        # ================= CREATE WORK =================
        work = Work(
            title=data.get("title"),
            workers=data.get("workers"),
            salary=data.get("salary"),
            date=data.get("date"),
            time=data.get("time"),
            phone=data.get("phone")
        )

        # ================= SAVE =================
        db.session.add(work)
        db.session.commit()

        # ================= LIVE UPDATE (IMPORTANT FIX) =================
        socketio.emit(
            "new_work",
            {
                "id": work.id,
                "title": work.title
            },
            broadcast=True  # 🔥 সব connected user এ যাবে
        )

        return work

    except Exception as e:
        db.session.rollback()
        print("Create Work Error:", e)  # debugging help
        return None
        
