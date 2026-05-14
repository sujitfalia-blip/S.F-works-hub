from extensions import db
from datetime import datetime


class Work(db.Model):

    __tablename__ = "works"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))
    description = db.Column(db.Text)

    workers = db.Column(db.String(50))
    salary = db.Column(db.String(100))

    date = db.Column(db.String(100))
    time = db.Column(db.String(100))

    phone = db.Column(db.String(20))
    location = db.Column(db.String(255))

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    status = db.Column(
        db.String(20),
        default="active"
    )

    is_deleted = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
