from models.work import Work
from extensions import db, socketio


def create_work(data, user_id):

    try:
        work = Work(
            title=data.get("title"),
            workers_needed=int(data.get("workers")),
            salary=int(data.get("salary")),
            date=data.get("date"),
            time=data.get("time"),
            phone=data.get("phone"),
            created_by=user_id
        )

        db.session.add(work)
        db.session.commit()

        # 🔥 LIVE UPDATE (IMPORTANT)
        socketio.emit(
            "new_work",
            {
                "id": work.id,
                "title": work.title
            },
            broadcast=True
        )

        return work

    except Exception as e:
        db.session.rollback()
        print("Create Work Error:", str(e))
        return None
        
