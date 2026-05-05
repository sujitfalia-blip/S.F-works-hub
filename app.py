from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from config import Config
from extensions import db, socketio

# 🔗 Routes
from routes.auth import auth
from routes.owner import owner
from routes.admin import admin_bp
from routes.super_admin import super_admin
from routes.user import user

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 🔌 Init extensions
    db.init_app(app)
    socketio.init_app(app)

    # ================= REGISTER ROUTES =================
    app.register_blueprint(auth)
    app.register_blueprint(owner)
    app.register_blueprint(admin_bp)
    app.register_blueprint(super_admin)
    app.register_blueprint(user)

    # ================= ERROR HANDLER =================
    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Page Not Found"}, 404

    @app.errorhandler(500)
    def server_error(e):
        return {"error": "Server Error"}, 500

    return app


# ✅ app instance
app = create_app()


# ================= DB INIT (SAFE WAY) =================
with app.app_context():
    db.create_all()


# ================= RUN =================
if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=False   # 🔥 production safe
    )
    