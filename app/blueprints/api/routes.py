"""API эндпоинты — для подсказок поиска, попапа товара, новостей по интересам и т.п."""
import io
from flask import jsonify, request, g, url_for, abort, send_file
from sqlalchemy import or_
from sqlalchemy import orm as sa_orm
from . import bp
from ...models import Product, News


@bp.route("/suggest")
def suggest():
    """Подсказки для поля поиска: сразу возвращает товары и новости по подстроке."""
    q = request.args.get("q", "").strip()
    if not q or len(q) < 2:
        return jsonify({"products": [], "news": []})
    like = f"%{q}%"
    products = Product.query.filter(or_(
        Product.name_ru.ilike(like), Product.name_en.ilike(like),
    )).limit(6).all()
    news = News.query.filter(or_(
        News.title_ru.ilike(like), News.title_en.ilike(like),
    )).limit(4).all()
    return jsonify({
        "products": [{"id": p.id, "name": p.name_ru, "name_en": p.name_en, "url": f"/catalog/{p.id}", "price": float(p.price)} for p in products],
        "news": [{"id": n.id, "title": n.title_ru, "title_en": n.title_en, "url": f"/news/{n.id}"} for n in news],
    })


@bp.route("/product/<int:product_id>")
def product_quick(product_id):
    """Компактный JSON для попапа товара («быстрый просмотр»)."""
    lang = getattr(g, "lang", "ru") or "ru"
    p = Product.query.get_or_404(product_id)
    if p.image == "db":
        image_url = url_for("api.product_image", product_id=p.id)
    else:
        image_url = url_for("static", filename="img/" + p.image)
    return jsonify({
        "id": p.id,
        "name": p.name(lang),
        "category": p.category.name(lang),
        "category_slug": p.category.slug,
        "image_url": image_url,
        "price": float(p.price),
        "old_price": float(p.old_price) if p.old_price else None,
        "short": p.short(lang) or (p.description(lang)[:240] if p.description(lang) else ""),
        "description": p.description(lang) or "",
        "in_stock": bool(p.in_stock),
        "stock": int(p.stock or 0),
        "has_audio": bool(p.has_audio) and p.category.slug == "vinyl",
        "audio_url": url_for("catalog.product_audio", product_id=p.id) if p.has_audio else None,
        "detail_url": url_for("catalog.detail", product_id=p.id),
        "add_url": url_for("cart.add", product_id=p.id),
        "avg_rating": p.avg_rating,
        "reviews_count": p.reviews_count,
    })


@bp.route("/product-image/<int:product_id>")
def product_image(product_id):
    """Отдаёт изображение товара из базы данных."""
    p = Product.query.options(sa_orm.undefer(Product.image_data)).get_or_404(product_id)
    if not p.image_data:
        abort(404)
    return send_file(
        io.BytesIO(p.image_data),
        mimetype=p.image_mime or "image/jpeg",
        max_age=86400,
    )


@bp.route("/news-image/<int:news_id>")
def news_image(news_id):
    """Отдаёт изображение новости из базы данных."""
    n = News.query.options(sa_orm.undefer(News.image_data)).get_or_404(news_id)
    if not n.image_data:
        abort(404)
    return send_file(
        io.BytesIO(n.image_data),
        mimetype=n.image_mime or "image/jpeg",
        max_age=86400,
    )


@bp.route("/external-news")
def external_news():
    """Псевдо-внешние новости."""
    items = News.query.order_by(News.rating.desc(), News.published_at.desc()).limit(5).all()
    return jsonify({
        "items": [
            {"id": n.id, "title_ru": n.title_ru, "title_en": n.title_en, "url": f"/news/{n.id}",
             "image": url_for("api.news_image", news_id=n.id) if n.image == "db" else url_for("static", filename="img/" + n.image),
             "rating": n.avg_rating}
            for n in items
        ]
    })