import os

class Config:

    # 🔐 Secret Key
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key")

    # 🗄️ PostgreSQL (Render)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://s_f_woraks_hub_user:G04Laksm3V7iFltkzjZH437L7vAST4VI@dpg-d7svrnpkh4rs739fbpfg-a.oregon-postgres.render.com/s_f_woraks_hub"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ⚡ Redis
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # 📁 Upload
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/uploads")

    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB

    # 🔒 Security
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
