"""API эндпоинты — для подсказок поиска, новостей по интересам и т.п."""
from flask import jsonify, request, g
from sqlalchemy import or_
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


@bp.route("/external-news")
def external_news():
    """Псевдо-внешние новости (для требования 'Подобрать новости по интересам из внешних источников').

    Без реального вызова внешнего API — возвращаем подборку из БД, отсортированную
    по рейтингу. На защите можно показать как заглушку под внешний RSS/News API.
    """
    items = News.query.order_by(News.rating.desc(), News.published_at.desc()).limit(5).all()
    return jsonify({
        "items": [
            {"id": n.id, "title_ru": n.title_ru, "title_en": n.title_en, "url": f"/news/{n.id}",
             "image": n.image, "rating": n.avg_rating}
            for n in items
        ]
    })
