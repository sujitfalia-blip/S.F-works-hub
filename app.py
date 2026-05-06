from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask
from config import Config
from extensions import db, socketio

# Routes
from routes.auth import auth
from routes.owner import owner
from routes.admin import admin_bp
from routes.super_admin import super_admin
from routes.user import user
from routes.main import main


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(owner)
    app.register_blueprint(admin_bp)
    app.register_blueprint(super_admin)
    app.register_blueprint(user)
    app.register_blueprint(main)

    return app


app = create_app()


# ================= ROUTE =================
@app.route("/")
def home():
    return "🔥 Server Running"


# ================= DB INIT (IMPORTANT FIX) =================
# ❌ Render এ create_all অনেক সময় crash করে
# তাই safe guard দিচ্ছি

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print("DB init skipped:", e)


# ================= RUN (LOCAL ONLY) =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=False)
