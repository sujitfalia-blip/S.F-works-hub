from models.work import Work
from extensions import db
from extensions import socketio

def create_work(data):

    # ================= CREATE WORK OBJECT =================
    work = Work(
        title=data.get("title"),
        workers=data.get("workers"),
        salary=data.get("salary"),
        date=data.get("date"),
        time=data.get("time"),
        phone=data.get("phone")
    )

    # ================= SAVE TO DB =================
    db.session.add(work)
    db.session.commit()

    # ================= LIVE UPDATE =================
    socketio.emit("new_work", {
        "id": work.id,
        "title": work.title
    })

    return work
  
