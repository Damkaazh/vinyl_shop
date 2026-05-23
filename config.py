"""Конфигурация приложения. Настройки берутся из переменных окружения / .env."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # База данных. По умолчанию SQLite в /instance/, легко поменять на PostgreSQL/MS SQL.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'vinyl_shop.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Загрузки (аватары, изображения товаров)
    UPLOAD_FOLDER = BASE_DIR / "app" / "static" / "uploads"
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 МБ — хватит для аудио-фрагментов и картинок
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    # Почта (SMTP)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "25"))
    MAIL_USE_TLS = bool(int(os.getenv("MAIL_USE_TLS", "0")))
    MAIL_USE_SSL = bool(int(os.getenv("MAIL_USE_SSL", "0")))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@vinylshop.local")
    MAIL_SUPPRESS_SEND = os.getenv("MAIL_SUPPRESS_SEND", "0") == "1"

    # Админ по умолчанию
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@vinylshop.local")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin12345")

    # Локализация (ru/en)
    LANGUAGES = ["ru", "en"]
    DEFAULT_LANGUAGE = "ru"
