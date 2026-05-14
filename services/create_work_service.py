from models.work_model import Work
from models.work_application_model import WorkApplication
from extensions import db, socketio


def create_work(data, user_id):
    try:
        work = Work(
            title=data.get("title"),
            workers=int(data.get("workers") or 0),
            salary=int(data.get("salary") or 0),
            date=data.get("date"),
            time=data.get("time"),
            phone=data.get("phone"),
            created_by=user_id
        )

        db.session.add(work)
        db.session.commit()

        # 🔥 SAFE SOCKET (Render stable fix)
        socketio.emit(
            "new_work",
            {
                "id": work.id,
                "title": work.title,
                "workers": work.workers,
                "salary": work.salary
            },
            broadcast=True,
            namespace="/"
        )

        return work

    except Exception as e:
        db.session.rollback()
        print("Create Work Error:", str(e))
        return None
        
