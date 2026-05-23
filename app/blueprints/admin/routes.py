"""Админ-панель: управление товарами, новостями, акциями, модерация отзывов."""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp
from ...extensions import db
from ...models import Product, Category, News, Promotion, Review, Order, User
from ...forms import ProductForm, NewsForm, PromotionForm
from ...utils import admin_required, save_upload


@bp.before_request
@login_required
def require_admin():
    if not current_user.is_admin:
        from flask import abort
        abort(403)


@bp.route("/")
def index():
    stats = {
        "products": Product.query.count(),
        "orders": Order.query.count(),
        "users": User.query.count(),
        "pending_reviews": Review.query.filter_by(is_approved=False).count(),
        "news": News.query.count(),
        "promotions": Promotion.query.count(),
    }
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    return render_template("admin/index.html", stats=stats, recent_orders=recent_orders)


# ===== Товары =====
@bp.route("/products")
def products():
    items = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("admin/products.html", items=items)


AUDIO_MIME_BY_EXT = {
    "mp3": "audio/mpeg",
    "ogg": "audio/ogg",
    "wav": "audio/wav",
    "m4a": "audio/mp4",
    "aac": "audio/aac",
}


def _read_audio_upload(file_storage):
    """Читает загруженный аудио-файл в (bytes, mime, original_name)."""
    if not file_storage or not hasattr(file_storage, "read"):
        return None
    name = getattr(file_storage, "filename", "")
    if not name:
        return None
    data = file_storage.read()
    if not data:
        return None
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    mime = AUDIO_MIME_BY_EXT.get(ext, getattr(file_storage, "mimetype", None) or "application/octet-stream")
    return data, mime, name


@bp.route("/products/new", methods=["GET", "POST"])
def product_new():
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name_ru) for c in Category.query.order_by(Category.id).all()]
    if form.validate_on_submit():
        try:
            image = save_upload(form.image.data, subdir="products") if form.image.data else None
            p = Product(
                category_id=form.category_id.data,
                name_ru=form.name_ru.data, name_en=form.name_en.data,
                short_ru=form.short_ru.data or "", short_en=form.short_en.data or "",
                description_ru=form.description_ru.data or "", description_en=form.description_en.data or "",
                specs_ru=form.specs_ru.data or "", specs_en=form.specs_en.data or "",
                price=form.price.data, old_price=form.old_price.data,
                stock=form.stock.data, is_featured=form.is_featured.data,
                image=image or "placeholder.svg",
            )
            audio = _read_audio_upload(form.audio.data)
            if audio:
                p.audio_data, p.audio_mime, p.audio_name = audio
            db.session.add(p)
            db.session.commit()
            flash("Товар добавлен.", "success")
            return redirect(url_for("admin.products"))
        except Exception as exc:
            db.session.rollback()
            from flask import current_app
            current_app.logger.exception("Не удалось сохранить товар")
            flash(f"Ошибка сохранения: {exc}", "danger")
    return render_template("admin/product_form.html", form=form, item=None)


@bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def product_edit(product_id):
    p = Product.query.get_or_404(product_id)
    form = ProductForm(obj=p)
    form.category_id.choices = [(c.id, c.name_ru) for c in Category.query.order_by(Category.id).all()]
    if form.validate_on_submit():
        try:
            image = save_upload(form.image.data, subdir="products") if form.image.data else None
            p.category_id = form.category_id.data
            p.name_ru, p.name_en = form.name_ru.data, form.name_en.data
            p.short_ru, p.short_en = form.short_ru.data or "", form.short_en.data or ""
            p.description_ru, p.description_en = form.description_ru.data or "", form.description_en.data or ""
            p.specs_ru, p.specs_en = form.specs_ru.data or "", form.specs_en.data or ""
            p.price = form.price.data
            p.old_price = form.old_price.data
            p.stock = form.stock.data
            p.is_featured = form.is_featured.data
            if image:
                p.image = image
            audio = _read_audio_upload(form.audio.data)
            if audio:
                p.audio_data, p.audio_mime, p.audio_name = audio
            if request.form.get("remove_audio"):
                p.audio_data, p.audio_mime, p.audio_name = None, None, None
            db.session.commit()
            flash("Товар обновлён.", "success")
            return redirect(url_for("admin.products"))
        except Exception as exc:
            db.session.rollback()
            from flask import current_app
            current_app.logger.exception("Не удалось обновить товар")
            flash(f"Ошибка сохранения: {exc}", "danger")
    return render_template("admin/product_form.html", form=form, item=p)


@bp.route("/products/<int:product_id>/delete", methods=["POST"])
def product_delete(product_id):
    p = Product.query.get_or_404(product_id)
    db.session.delete(p)
    db.session.commit()
    flash("Товар удалён.", "info")
    return redirect(url_for("admin.products"))


# ===== Новости =====
@bp.route("/news")
def news_list():
    items = News.query.order_by(News.published_at.desc()).all()
    return render_template("admin/news.html", items=items)


@bp.route("/news/new", methods=["GET", "POST"])
def news_new():
    form = NewsForm()
    if form.validate_on_submit():
        image = save_upload(form.image.data, subdir="news") if form.image.data else None
        n = News(
            title_ru=form.title_ru.data, title_en=form.title_en.data,
            body_ru=form.body_ru.data, body_en=form.body_en.data,
            is_featured=form.is_featured.data, image=image or "news-default.svg",
        )
        db.session.add(n)
        db.session.commit()
        flash("Новость добавлена.", "success")
        return redirect(url_for("admin.news_list"))
    return render_template("admin/news_form.html", form=form, item=None)


@bp.route("/news/<int:news_id>/edit", methods=["GET", "POST"])
def news_edit(news_id):
    n = News.query.get_or_404(news_id)
    form = NewsForm(obj=n)
    if form.validate_on_submit():
        image = save_upload(form.image.data, subdir="news") if form.image.data else None
        n.title_ru, n.title_en = form.title_ru.data, form.title_en.data
        n.body_ru, n.body_en = form.body_ru.data, form.body_en.data
        n.is_featured = form.is_featured.data
        if image:
            n.image = image
        db.session.commit()
        flash("Новость обновлена.", "success")
        return redirect(url_for("admin.news_list"))
    return render_template("admin/news_form.html", form=form, item=n)


@bp.route("/news/<int:news_id>/delete", methods=["POST"])
def news_delete(news_id):
    n = News.query.get_or_404(news_id)
    db.session.delete(n)
    db.session.commit()
    flash("Новость удалена.", "info")
    return redirect(url_for("admin.news_list"))


# ===== Акции =====
@bp.route("/promotions")
def promotions():
    items = Promotion.query.order_by(Promotion.created_at.desc()).all()
    return render_template("admin/promotions.html", items=items)


@bp.route("/promotions/new", methods=["GET", "POST"])
def promotion_new():
    form = PromotionForm()
    if form.validate_on_submit():
        image = save_upload(form.image.data, subdir="promotions") if form.image.data else None
        pr = Promotion(
            title_ru=form.title_ru.data, title_en=form.title_en.data,
            body_ru=form.body_ru.data, body_en=form.body_en.data,
            discount_percent=form.discount_percent.data or 0,
            valid_until=form.valid_until.data,
            image=image or "promo-default.svg",
        )
        db.session.add(pr)
        db.session.commit()
        flash("Акция добавлена.", "success")
        return redirect(url_for("admin.promotions"))
    return render_template("admin/promotion_form.html", form=form, item=None)


@bp.route("/promotions/<int:promo_id>/delete", methods=["POST"])
def promotion_delete(promo_id):
    pr = Promotion.query.get_or_404(promo_id)
    db.session.delete(pr)
    db.session.commit()
    flash("Акция удалена.", "info")
    return redirect(url_for("admin.promotions"))


# ===== Модерация отзывов =====
@bp.route("/reviews")
def reviews():
    pending = Review.query.filter_by(is_approved=False).order_by(Review.created_at.desc()).all()
    approved = Review.query.filter_by(is_approved=True).order_by(Review.created_at.desc()).limit(50).all()
    return render_template("admin/reviews.html", pending=pending, approved=approved)


@bp.route("/reviews/<int:review_id>/approve", methods=["POST"])
def review_approve(review_id):
    r = Review.query.get_or_404(review_id)
    r.is_approved = True
    db.session.commit()
    flash("Отзыв опубликован.", "success")
    return redirect(url_for("admin.reviews"))


@bp.route("/reviews/<int:review_id>/delete", methods=["POST"])
def review_delete(review_id):
    r = Review.query.get_or_404(review_id)
    db.session.delete(r)
    db.session.commit()
    flash("Отзыв удалён.", "info")
    return redirect(url_for("admin.reviews"))


# ===== Заказы =====
@bp.route("/orders")
def orders():
    items = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin/orders.html", items=items)


@bp.route("/orders/<int:order_id>/status", methods=["POST"])
def order_status(order_id):
    o = Order.query.get_or_404(order_id)
    o.status = request.form.get("status", o.status)
    db.session.commit()
    flash("Статус заказа обновлён.", "success")
    return redirect(url_for("admin.orders"))
