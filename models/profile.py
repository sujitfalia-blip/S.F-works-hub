from extensions import db
from datetime import datetime


class Profile(db.Model):
    __tablename__ = "profile"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        unique=True,
        nullable=False
    )

    user = db.relationship(
        'User',
        backref=db.backref('profile', uselist=False)
    )

    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    age = db.Column(db.Integer)
    education = db.Column(db.String(100))
    area = db.Column(db.String(100))
    gender = db.Column(db.String(20))
    religion = db.Column(db.String(50))
    country = db.Column(db.String(50))
    work_desc = db.Column(db.Text)

    profile_img = db.Column(db.String(200))
    cover_img = db.Column(db.String(200))

    gallery = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
