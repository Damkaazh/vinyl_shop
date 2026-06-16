"""Маршруты главного блюпринта."""
from flask import render_template, g, request, jsonify, url_for
from sqlalchemy import or_
from . import bp
from ...models import Product, News, Promotion, Category


@bp.route("/")
def index():
    featured_products = Product.query.filter_by(is_featured=True).limit(8).all()
    featured_news = News.query.filter_by(is_featured=True).order_by(News.published_at.desc()).limit(4).all()
    promotions = Promotion.query.order_by(Promotion.created_at.desc()).limit(6).all()
    categories = Category.query.order_by(Category.id).all()

    slider_items = []
    for p in featured_products[:5]:
        slider_items.append({
            "kind": "product",
            "id": p.id,
            "image": url_for("api.product_image", product_id=p.id) if p.image == "db" else url_for("static", filename="img/" + p.image),
            "title_ru": p.name_ru, "title_en": p.name_en,
            "short_ru": p.short_ru or p.name_ru,
            "short_en": p.short_en or p.name_en,
            "url": f"/catalog/{p.id}",
            "price": float(p.price),
        })
    for n in featured_news[:3]:
        slider_items.append({
            "kind": "news",
            "id": n.id,
            "image": url_for("static", filename="img/news/" + n.image) if n.image and not n.image.startswith("/") and not n.image.startswith("http") else (n.image or ""),
            "title_ru": n.title_ru, "title_en": n.title_en,
            "short_ru": (n.body_ru or "")[:160],
            "short_en": (n.body_en or "")[:160],
            "url": f"/news/{n.id}",
        })
    return render_template(
        "index.html",
        slider_items=slider_items,
        featured_products=featured_products,
        featured_news=featured_news,
        promotions=promotions,
        categories=categories,
    )


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/news")
def news_list():
    items = News.query.order_by(News.published_at.desc()).all()
    return render_template("news_list.html", news_items=items)


@bp.route("/news/<int:news_id>")
def news_detail(news_id):
    item = News.query.get_or_404(news_id)
    return render_template("news_detail.html", item=item)


@bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    products = []
    news_items = []
    if q:
        like = f"%{q}%"
        products = Product.query.filter(or_(
            Product.name_ru.ilike(like),
            Product.name_en.ilike(like),
            Product.description_ru.ilike(like),
            Product.description_en.ilike(like),
        )).limit(40).all()
        news_items = News.query.filter(or_(
            News.title_ru.ilike(like),
            News.title_en.ilike(like),
            News.body_ru.ilike(like),
            News.body_en.ilike(like),
        )).limit(20).all()
    return render_template("search.html", q=q, products=products, news_items=news_items)