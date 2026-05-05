import os

class Config:

    # 🔐 Secret Key (env থেকে)
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key")

    # 🗄️ Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost/sfhub"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ⚡ Redis
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # 📁 Upload
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/uploads")

    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB

    # 🔒 Security
    SESSION_COOKIE_SECURE = False   # True (production https হলে)
    SESSION_COOKIE_HTTPONLY = True
    