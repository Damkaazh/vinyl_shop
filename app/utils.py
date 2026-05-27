"""Утилиты: загрузка файлов, отправка писем, декораторы."""
import secrets
import threading
from datetime import datetime
from functools import wraps
from pathlib import Path
from flask import current_app, abort, render_template
from flask_login import current_user
from flask_mail import Message
from werkzeug.utils import secure_filename
from .extensions import mail


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]
    )


def save_upload(file_storage, subdir=""):
    """Сохраняет файл с уникальным именем, возвращает имя файла."""
    filename = getattr(file_storage, "filename", None)
    if not file_storage or not filename or not hasattr(file_storage, "save"):
        return None
    if not allowed_file(filename):
        return None
    ext = filename.rsplit(".", 1)[1].lower()
    new_name = f"{secrets.token_hex(8)}.{ext}"
    folder = Path(current_app.config["UPLOAD_FOLDER"]) / subdir if subdir else Path(current_app.config["UPLOAD_FOLDER"])
    folder.mkdir(parents=True, exist_ok=True)
    filepath = folder / secure_filename(new_name)
    file_storage.save(filepath)
    rel = str(Path(subdir) / new_name) if subdir else new_name
    return rel.replace("\\", "/")


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def _send_email(recipient: str, subject: str, text_body: str, html_body: str | None = None) -> bool:
    """Универсальная отправка письма. Нет SMTP — пишет в instance/emails.log."""
    sender = current_app.config.get("MAIL_DEFAULT_SENDER")
    suppress = current_app.config.get("MAIL_SUPPRESS_SEND")
    smtp_user = current_app.config.get("MAIL_USERNAME")
    log_path = Path(current_app.instance_path) / "emails.log"

    if suppress or not smtp_user:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n=== TO: {recipient} | SUBJECT: {subject} ===\n{text_body}\n")
        return False

    msg = Message(subject=subject, recipients=[recipient], sender=sender)
    msg.body = text_body
    if html_body:
        msg.html = html_body

    app = current_app._get_current_object()

    def _send():
        with app.app_context():
            try:
                mail.send(msg)
            except Exception as e:
                app.logger.error(f"Mail send failed: {e}")
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(f"\n=== FAILED TO: {recipient} | {e} ===\n{text_body}\n")

    threading.Thread(target=_send, daemon=True).start()
    return True


def send_order_email(order):
    """Письмо-подтверждение заказа."""
    subject = f"Заказ №{order.id} в магазине «Виниловая Гавань»"
    html = render_template("emails/order_confirmation.html", order=order)
    text = render_template("emails/order_confirmation.txt", order=order)
    return _send_email(order.email, subject, text, html)


def send_welcome_email(user):
    """Приветственное письмо после регистрации."""
    subject = "Добро пожаловать в «Виниловую Гавань»"
    html = render_template("emails/welcome.html", user=user)
    text = render_template("emails/welcome.txt", user=user)
    return _send_email(user.email, subject, text, html)


def send_login_notification(user, ip: str = "", user_agent: str = ""):
    """Уведомление о входе в аккаунт."""
    subject = "Вход в аккаунт «Виниловая Гавань»"
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    html = render_template("emails/login_alert.html", user=user, ip=ip, user_agent=user_agent, now_str=now_str)
    text = render_template("emails/login_alert.txt", user=user, ip=ip, user_agent=user_agent, now_str=now_str)
    return _send_email(user.email, subject, text, html)

def _send():
    with app.app_context():
        try:
            mail.send(msg)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n=== SENT OK TO: {recipient} | {subject} ===\n")
        except Exception as e:
            app.logger.error(f"Mail send failed: {e}")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n=== FAILED TO: {recipient} | {e} ===\n")