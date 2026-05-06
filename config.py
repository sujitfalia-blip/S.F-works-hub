import os

class Config:

    # 🔐 Secret Key
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key")

    # 🗄️ PostgreSQL (Render safe fix)
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        # Render sometimes gives postgres:// instead of postgresql://
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace("postgres://", "postgresql://")
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///local.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ⚡ Redis
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # 📁 Upload folder
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/uploads")

    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB

    # 🔒 Session security
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
