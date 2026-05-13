"""Фабрика Flask-приложения."""
import os
from pathlib import Path
from flask import Flask, request, session, g
from config import Config
from .extensions import db, login_manager, mail, migrate


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_class)

    # Ensure folders exist
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    # Регистрация блюпринтов
    from .blueprints.main import bp as main_bp
    from .blueprints.auth import bp as auth_bp
    from .blueprints.catalog import bp as catalog_bp
    from .blueprints.cart import bp as cart_bp
    from .blueprints.account import bp as account_bp
    from .blueprints.admin import bp as admin_bp
    from .blueprints.api import bp as api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(catalog_bp, url_prefix="/catalog")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(account_bp, url_prefix="/account")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Контекст шаблонов: текущий язык, переводы
    from .i18n import get_locale, translations

    @app.before_request
    def set_locale():
        lang = request.args.get("lang")
        if lang in app.config["LANGUAGES"]:
            session["lang"] = lang
        g.lang = session.get("lang", app.config["DEFAULT_LANGUAGE"])

    @app.context_processor
    def inject_globals():
        from .models import Category
        return {
            "lang": g.get("lang", "ru"),
            "t": translations(g.get("lang", "ru")),
            "categories_nav": Category.query.order_by(Category.id).all(),
        }

    # Обработчики ошибок
    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template("errors/404.html"), 404

    # Создаём таблицы и сидим демо-данные при первом запуске
    with app.app_context():
        db.create_all()
        from .seed import seed_if_empty
        seed_if_empty()

    return app
