from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import or_
from . import bp
from ...extensions import db
from ...forms import RegistrationForm, LoginForm, ForgotPasswordForm
from ...models import User, LoginSession
from ...utils import save_upload, send_welcome_email, send_login_notification


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Проверка уникальности
        existing = User.query.filter(or_(
            User.email == form.email.data,
            User.login == form.login.data,
            User.nickname == form.nickname.data,
        )).first()
        if existing:
            if existing.email == form.email.data:
                form.email.errors.append("Этот e-mail уже занят.")
            elif existing.login == form.login.data:
                form.login.errors.append("Этот логин уже занят.")
            else:
                form.nickname.errors.append("Этот никнейм уже занят.")
            return render_template("auth/register.html", form=form)

        avatar = save_upload(form.avatar.data, subdir="avatars") if form.avatar.data else None

        user = User(
            email=form.email.data,
            login=form.login.data,
            full_name=form.full_name.data,
            nickname=form.nickname.data,
            birth_date=form.birth_date.data,
            gender=form.gender.data,
            avatar=avatar or "default-avatar.svg",
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        _record_session(user)
        try:
            send_welcome_email(user)
        except Exception:
            pass  # письмо не должно ломать регистрацию
        flash("Регистрация прошла успешно. Добро пожаловать!", "success")
        return redirect(url_for("account.index"))
    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        ident = form.identifier.data.strip()
        user = User.query.filter(or_(User.email == ident, User.login == ident)).first()
        if not user or not user.check_password(form.password.data):
            flash("Неверный e-mail/логин или пароль.", "danger")
            return render_template("auth/login.html", form=form)
        login_user(user, remember=form.remember.data)
        _record_session(user)
        try:
            send_login_notification(
                user,
                ip=request.headers.get("X-Forwarded-For", request.remote_addr or ""),
                user_agent=request.user_agent.string if request.user_agent else "",
            )
        except Exception:
            pass  # письмо не должно ломать вход
        flash("Вход выполнен.", "success")
        next_url = request.args.get("next") or url_for("account.index")
        return redirect(next_url)
    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта.", "info")
    return redirect(url_for("main.index"))


@bp.route("/forgot", methods=["GET", "POST"])
def forgot():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        # Демо: показываем сообщение об отправке (учебный проект)
        flash("Если такой e-mail зарегистрирован, мы отправили на него письмо для восстановления.", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/forgot.html", form=form)


def _record_session(user):
    sess = LoginSession(
        user_id=user.id,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string[:255] if request.user_agent else None,
    )
    db.session.add(sess)
    db.session.commit()
