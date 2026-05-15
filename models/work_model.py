from datetime import datetime
from extensions import db


class Work(db.Model):
    __tablename__ = "works"

    id = db.Column(db.Integer, primary_key=True)

    # 🧾 Work Title (যেমন: 10 জন রাজমিস্ত্রি লাগবে)
    title = db.Column(db.String(200), nullable=False)

    # 📝 Full description
    description = db.Column(db.Text, nullable=False)

    # 📱 Mandatory mobile number
    mobile = db.Column(db.String(15), nullable=False)

    # 👤 User ID who posted this work
    user_id = db.Column(db.Integer, nullable=False, index=True)

    # 🔄 Status control (admin/owner approval system)
    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending"
    )
    # possible values:
    # pending -> not approved yet
    # approved -> visible to users
    # rejected -> removed by owner

    # ⏱️ Timestamp
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # 🔥 Optional: update time (professional upgrade)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Work {self.id} - {self.title} ({self.status})>"
