from datetime import datetime
from extensions import db


class Work(db.Model):

    __tablename__ = "works"

    # ================= PRIMARY KEY =================
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ================= WORK INFO =================
    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    =========================
    # FOREIGN KEY
    # =========================
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # =========================
    # RELATIONSHIP
    # =========================
    user = db.relationship(
        'User',
        back_populates='works'
    )

    # ================= CONTACT =================
    mobile = db.Column(
        db.String(15),
        nullable=False
    )

    # ================= USER =================
    user_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    # ================= STATUS =================
    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending"
    )
    # pending
    # approved
    # rejected
    # deleted

    # ================= ACTIVE =================
    is_active = db.Column(
        db.Boolean,
        default=False
    )

    # ================= SOFT DELETE =================
    is_deleted = db.Column(
        db.Boolean,
        default=False
    )

    # ================= EDIT TRACKING =================
    edit_count = db.Column(
        db.Integer,
        default=0
    )

    # ================= OWNER ACTION =================
    approved_by = db.Column(
        db.Integer,
        nullable=True
    )

    rejected_by = db.Column(
        db.Integer,
        nullable=True
    )

    edited_by = db.Column(
        db.Integer,
        nullable=True
    )

    # ================= TIMESTAMP =================
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ================= STRING =================
    def __repr__(self):

        return (
            f"<Work "
            f"{self.id} | "
            f"{self.title} | "
            f"{self.status}>"
    )
