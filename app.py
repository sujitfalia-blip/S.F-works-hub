import eventlet
eventlet.monkey_patch()

from dotenv import load_dotenv
load_dotenv()

import os

from flask import Flask

from config import Config

from extensions import db, socketio
from sqlalchemy import text

# ✅ ADD THIS
from flask_migrate import Migrate

# ================= ROUTES =================
from routes.auth import auth
from routes.owner import owner
from routes.admin import admin_bp
from routes.super_admin import super_admin
from routes.user import user
from routes.main import main
from routes.work import work as work_bp



# ================= CREATE APP =================
def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    # ================= INIT EXTENSIONS =================
    db.init_app(app)

    socketio.init_app(
        app,
        cors_allowed_origins="*"
    )

    # ✅ ADD THIS
    migrate = Migrate(app, db)

    # ================= REGISTER BLUEPRINTS =================
    app.register_blueprint(auth)

    app.register_blueprint(owner)

    app.register_blueprint(admin_bp)

    app.register_blueprint(super_admin)

    app.register_blueprint(user)

    app.register_blueprint(main)
    
    app.register_blueprint(work_bp)
    return app


# ================= APP =================
app = create_app()


# ==============app.register_blueprint(work_bp)=== SAFE DB INIT =================
with app.app_context():

    try:

        db.session.execute(text("""
            ALTER TABLE "user"
            ALTER COLUMN email DROP NOT NULL;
        """))

        db.session.commit()

        print("✅ Email column fixed")

    except Exception as e:

        print("DB fix skipped:", e)

    try:

        db.create_all()

        print("✅ Database connected")

    except Exception as e:

        print("❌ DB init skipped:", e)

# ================= RUN LOCAL =================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=False
    )
