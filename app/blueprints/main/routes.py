from flask import render_template, g, request
from sqlalchemy import or_
from . import bp
from ...models import Product, News, Promotion, Category


@bp.route("/")
def index():
    lang = getattr(g, "lang", "ru") or "ru"

    featured_products = Product.query.filter_by(isfeatured=True).limit(8).all()
    featured_news = News.query.filter_by(isfeatured=True).order_by(News.publishedat.desc()).limit(4).all()
    promotions = Promotion.query.order_by(Promotion.createdat.desc()).limit(6).all()
    categories = Category.query.order_by(Category.id).all()

    slider_items = []

    for p in featured_products[:5]:
        slider_items.append({
            "kind": "product",
            "id": p.id,
            "image": p.image,
            "title": p.name(lang),
            "short": p.short(lang) or p.name(lang),
            "url": f"/catalog/{p.id}",
            "price": float(p.price),
            "oldprice": float(p.oldprice) if p.oldprice else None,
            "has_db_image": p.hasdbimage,
            "rating": p.avgrating,
            "reviews_count": p.reviewscount,
            "in_stock": p.instock,
        })

    for n in featured_news[:3]:
        body = n.body(lang) or ""
        slider_items.append({
            "kind": "news",
            "id": n.id,
            "image": n.image,
            "title": n.title(lang),
            "short": body[:160],
            "url": f"/news/{n.id}",
            "rating": n.avgrating,
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
    items = News.query.order_by(News.publishedat.desc()).all()
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
            Product.nameru.ilike(like),
            Product.nameen.ilike(like),
            Product.descriptionru.ilike(like),
            Product.descriptionen.ilike(like),
            Product.shortru.ilike(like),
            Product.shorten.ilike(like),
            Product.specsru.ilike(like),
            Product.specsen.ilike(like),
        )).limit(40).all()

        news_items = News.query.filter(or_(
            News.titleru.ilike(like),
            News.titleen.ilike(like),
            News.bodyru.ilike(like),
            News.bodyen.ilike(like),
        )).limit(20).all()

    return render_template("search.html", q=q, products=products, news_items=news_items)