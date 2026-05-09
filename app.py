from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask
from config import Config
from extensions import db, socketio
from flask_migrate import Migrate
from sqlalchemy import text

# Routes
from routes.auth import auth
from routes.owner import owner
from routes.admin import admin_bp
from routes.super_admin import super_admin
from routes.user import user
from routes.main import main
from routes.work import work as work_bp
from routes.profile import profile_bp
from routes.admin_tools import admin_tools



# ================= APP =================
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ================= SAFE UPLOAD FOLDER =================
    upload_path = app.config.get('UPLOAD_FOLDER')

    if upload_path and not os.path.exists(upload_path):
        os.makedirs(upload_path)

    # ================= EXTENSIONS =================
    db.init_app(app)

    socketio.init_app(
        app,
        cors_allowed_origins="*",
        async_mode="gevent"
    )

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
    app.register_blueprint(work_bp)

    return app


app = create_app()


# ================= DB PATCH =================
with app.app_context():
    try:
        db.session.execute(text("""
            ALTER TABLE "user"
            ALTER COLUMN email DROP NOT NULL;
        """))
        db.session.commit()
        print("DB patch applied")
    except Exception as e:
        print("DB patch skipped:", e)


# ================= RUN =================
if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
