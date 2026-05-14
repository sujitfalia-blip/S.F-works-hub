from gevent import monkey
monkey.patch_all()

from dotenv import load_dotenv
load_dotenv()

import os

from flask import Flask
from flask_socketio import emit, join_room
from flask_login import current_user, LoginManager

from config import Config
from extensions import db, socketio

from flask_migrate import Migrate

import cloudinary
import cloudinary.uploader

# ================= MODELS =================

from models.chat import Chat
from models.user import User
from models.work_model import Work

# ================= ROUTES =================

from routes.auth import auth
from routes.owner import owner
from routes.admin import admin_bp
from routes.super_admin import super_admin
from routes.user import user
from routes.main import main
from routes.work_routes import work
from routes.booking_control import booking
from routes.profile import profile_bp
from routes.admin_tools import admin_tools

# ================= LOGIN MANAGER =================

login_manager = LoginManager()
login_manager.login_view = "auth.login"

# ================= CREATE APP =================

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    # ================= LOGIN =================

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ================= CLOUDINARY =================

    cloudinary.config(
        cloud_name="dion15zps",
        api_key="136556886157942",
        api_secret="MBvKiT2EFaCzm9BGB9K1itfmiDU",
        secure=True
    )

    # ================= MAX UPLOAD =================

    app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

    # ================= UPLOAD FOLDER =================

    upload_path = app.config.get("UPLOAD_FOLDER")

    if upload_path:

        if os.path.exists(upload_path) and not os.path.isdir(upload_path):
            os.remove(upload_path)

        os.makedirs(upload_path, exist_ok=True)

    # ================= DATABASE =================

    db.init_app(app)

    # ================= SOCKET IO =================

    socketio.init_app(
        app,
        cors_allowed_origins="*",
        async_mode="gevent"
    )

    # ================= MIGRATION =================

    Migrate(app, db)

    # ================= BLUEPRINTS =================

    app.register_blueprint(auth)
    app.register_blueprint(owner)
    app.register_blueprint(admin_bp)
    app.register_blueprint(super_admin)
    app.register_blueprint(user)
    app.register_blueprint(main)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_tools)
    app.register_blueprint(work)
    app.register_blueprint(booking)

    return app


# ================= APP =================

app = create_app()

# =====================================================
# ================= DATABASE AUTO FIX ==================
# =====================================================

with app.app_context():

    # ================= CREATE ALL TABLES =================

    db.create_all()

    try:

        # ================= USER TABLE FIX =================

        db.session.execute(db.text("""
            ALTER TABLE "user"
            ADD COLUMN IF NOT EXISTS profile_img TEXT
        """))

        db.session.execute(db.text("""
            ALTER TABLE "user"
            ADD COLUMN IF NOT EXISTS is_online BOOLEAN DEFAULT FALSE
        """))

        db.session.execute(db.text("""
            ALTER TABLE "user"
            ADD COLUMN IF NOT EXISTS last_seen TIMESTAMP
        """))

        db.session.execute(db.text("""
            ALTER TABLE "user"
            ADD COLUMN IF NOT EXISTS socket_id VARCHAR(100)
        """))

        # ================= CHAT TABLE FIX =================

        db.session.execute(db.text("""
            ALTER TABLE chat
            ADD COLUMN IF NOT EXISTS is_read BOOLEAN DEFAULT FALSE
        """))

        db.session.execute(db.text("""
            ALTER TABLE chat
            ADD COLUMN IF NOT EXISTS read_at TIMESTAMP
        """))

        db.session.execute(db.text("""
            ALTER TABLE chat
            ADD COLUMN IF NOT EXISTS is_typing BOOLEAN DEFAULT FALSE
        """))

        db.session.execute(db.text("""
            ALTER TABLE chat
            ADD COLUMN IF NOT EXISTS typing_at TIMESTAMP
        """))

        db.session.execute(db.text("""
            ALTER TABLE chat
            ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE
        """))

        db.session.execute(db.text("""
            ALTER TABLE chat
            ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP
        """))

        db.session.commit()

        print("✅ Missing columns added successfully")

    except Exception as e:

        print("❌ DB Update Error:", str(e))

    print("✅ All tables created")


# =====================================================
# ================= SOCKET EVENTS =====================
# =====================================================

# ================= USER CONNECT =================

@socketio.on("connect")
def handle_connect():

    try:

        if current_user.is_authenticated:

            current_user.is_online = True

            db.session.commit()

            print(f"✅ User Online: {current_user.id}")

    except Exception as e:

        print("❌ Connect Error:", str(e))


# ================= USER DISCONNECT =================

@socketio.on("disconnect")
def handle_disconnect():

    try:

        if current_user.is_authenticated:

            current_user.is_online = False

            db.session.commit()

            print(f"❌ User Offline: {current_user.id}")

    except Exception as e:

        print("❌ Disconnect Error:", str(e))


# ================= JOIN ROOM =================

@socketio.on("join")
def on_join(data):

    if not current_user.is_authenticated:
        return

    user_id = current_user.id

    room = f"chat_{min(user_id, int(data['user_id']))}_{max(user_id, int(data['user_id']))}"

    join_room(room)

    print(f"✅ Joined Room: {room}")


# ================= SEND MESSAGE =================
@socketio.on("send_message")
def handle_send_message(data):

    if not current_user.is_authenticated:
        return

    try:
        receiver_id = data.get("receiver_id")
        message = data.get("message")

        if not receiver_id or not message:
            return

        receiver_id = int(receiver_id)
        sender_id = current_user.id

        # ================= SAVE =================
        chat = Chat(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=message.strip()
        )

        db.session.add(chat)
        db.session.commit()

        # ================= ROOM (WHATSAPP STYLE) =================
        room = f"chat_{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"

        response = {
            "id": chat.id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "message": chat.message,
            "created_at": str(chat.created_at)
        }

        emit("receive_message", response, room=room)

        print("✅ Message Sent")

    except Exception as e:
        print("❌ Chat Error:", str(e))

# ================= MESSAGE READ =================

@socketio.on("mark_read")
def mark_read(data):

    try:

        message_id = data.get("message_id")

        if not message_id:
            return

        message = Chat.query.get(message_id)

        if message:

            message.is_read = True

            db.session.commit()

            emit(
                "message_read",
                {
                    "message_id": message.id
                },
                room=f"chat_{message.sender_id}"
            )

            print("✅ Message Read")

    except Exception as e:

        print("❌ Read Error:", str(e))


# ================= TYPING =================

@socketio.on("typing")
def typing(data):

    try:

        if not current_user.is_authenticated:
            return

        receiver_id = data.get("receiver_id")

        if not receiver_id:
            return

        room = f"chat_{receiver_id}"

        emit(
            "typing",
            {
                "user_id": current_user.id
            },
            room=room
        )

    except Exception as e:

        print("❌ Typing Error:", str(e))


# ================= STOP TYPING =================

@socketio.on("stop_typing")
def stop_typing(data):

    try:

        if not current_user.is_authenticated:
            return

        receiver_id = data.get("receiver_id")

        if not receiver_id:
            return

        room = f"chat_{receiver_id}"

        emit(
            "stop_typing",
            {
                "user_id": current_user.id
            },
            room=room
        )

    except Exception as e:

        print("❌ Stop Typing Error:", str(e))


# ================= RUN =================

if __name__ == "__main__":

    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
