from extensions import db
from datetime import datetime


class Work(db.Model):

    __tablename__ = "works"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    salary = db.Column(
        db.String(100)
    )

    location = db.Column(
        db.String(200)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<Work {self.title}>"
