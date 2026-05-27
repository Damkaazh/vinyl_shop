"""Конфигурация приложения. Настройки берутся из переменных окружения / .env."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _normalize_db_url(url: str) -> str:
    """Render выдаёт DATABASE_URL в формате postgres://, но SQLAlchemy 2.x требует postgresql://.
    Также добавляем явный драйвер psycopg2 для предсказуемости."""
    if not url:
        return url
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://") and "+psycopg2" not in url.split("://", 1)[0]:
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]
    return url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # База данных. По умолчанию SQLite в /instance/, легко поменять на PostgreSQL/MS SQL.
    SQLALCHEMY_DATABASE_URI = _normalize_db_url(
        os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'vinyl_shop.db'}")
    )
    # На Render Postgres-соединения рвутся по idle — pool_pre_ping и короткий recycle спасают от SSL EOF.
    # keepalives в connect_args держат TCP-соединение живым, чтобы CDN/firewall его не обрывал.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 180,
        "pool_size": 5,
        "max_overflow": 5,
        "pool_timeout": 30,
        "connect_args": {
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        } if os.getenv("DATABASE_URL", "").startswith(("postgres://", "postgresql://")) else {},
    }
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
