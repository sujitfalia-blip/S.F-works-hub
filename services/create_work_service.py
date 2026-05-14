from models.work_model import Work
from extensions import db, socketio


def create_work(data, user_id):

    try:

        # =========================
        # CREATE WORK
        # =========================
        work = Work(

            title=data.get("title"),

            description=data.get(
                "description",
                "No description"
            ),

            workers=data.get("workers"),

            salary=data.get("salary"),

            date=data.get("date"),

            time=data.get("time"),

            phone=data.get("phone"),

            user_id=user_id
        )

        # =========================
        # SAVE DATABASE
        # =========================
        db.session.add(work)
        db.session.commit()

        # =========================
        # SOCKET EMIT
        # =========================
        try:

            socketio.emit(
                "new_work",
                {
                    "id": work.id,
                    "title": work.title,
                    "workers": work.workers,
                    "salary": work.salary
                },
                namespace="/"
            )

        except Exception as socket_error:

            print(
                "Socket Error:",
                str(socket_error)
            )

        return work

    except Exception as e:

        db.session.rollback()

        print(
            "Create Work Error:",
            str(e)
        )

        return None
