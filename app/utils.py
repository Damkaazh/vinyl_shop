"""Утилиты: загрузка файлов, отправка писем, декораторы."""
import os
import secrets
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
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        return None
    ext = file_storage.filename.rsplit(".", 1)[1].lower()
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


def send_order_email(order):
    """Отправляет покупателю письмо с подтверждением заказа.

    Если SMTP не настроен — пишет письмо в файл /instance/emails.log,
    чтобы можно было показать функционал на защите ВКР.
    """
    subject = f"Заказ №{order.id} в магазине «Виниловая Гавань»"
    html = render_template("emails/order_confirmation.html", order=order)
    text = render_template("emails/order_confirmation.txt", order=order)

    sender = current_app.config.get("MAIL_DEFAULT_SENDER")
    suppress = current_app.config.get("MAIL_SUPPRESS_SEND")
    smtp_user = current_app.config.get("MAIL_USERNAME")

    if suppress or not smtp_user:
        # Имитация — записываем в лог
        log_path = Path(current_app.instance_path) / "emails.log"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n=== TO: {order.email} | SUBJECT: {subject} ===\n{text}\n")
        return False

    msg = Message(subject=subject, recipients=[order.email], sender=sender)
    msg.body = text
    msg.html = html
    try:
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Mail send failed: {e}")
        log_path = Path(current_app.instance_path) / "emails.log"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n=== FAILED TO: {order.email} | {e} ===\n{text}\n")
        return False
