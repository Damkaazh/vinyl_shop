from datetime import datetime

from flask import render_template, request, redirect, url_for, flash, abort, g, Response
from flask_login import current_user
from sqlalchemy import or_
from . import bp
from ...extensions import db
from ...models import Product, Category, Review, RecentlyViewed
from ...forms import ReviewForm


@bp.route("/")
def index():
    return _list_products(category_slug=None)


@bp.route("/category/<slug>")
def category(slug):
    return _list_products(category_slug=slug)


def _list_products(category_slug=None):
    query = Product.query
    category_obj = None

    if category_slug:
        category_obj = Category.query.filter_by(slug=category_slug).first_or_404()
        query = query.filter(Product.categoryid == category_obj.id)

    q = request.args.get("q", "").strip()
    available = request.args.get("available")
    price_min = request.args.get("price_min", type=float)
    price_max = request.args.get("price_max", type=float)
    sort = request.args.get("sort", "new")

    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            Product.nameru.ilike(like),
            Product.nameen.ilike(like),
            Product.descriptionru.ilike(like),
            Product.descriptionen.ilike(like),
            Product.shortru.ilike(like),
            Product.shorten.ilike(like),
            Product.specsru.ilike(like),
            Product.specsen.ilike(like),
        ))

    if available:
        query = query.filter(Product.stock > 0)

    if price_min is not None:
        query = query.filter(Product.price >= price_min)

    if price_max is not None:
        query = query.filter(Product.price <= price_max)

    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
        products = query.all()

    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
        products = query.all()

    elif sort == "rating":
        products = query.all()
        products.sort(key=lambda p: p.avgrating, reverse=True)

    else:
        query = query.order_by(Product.createdat.desc())
        products = query.all()

    return render_template(
        "catalog/list.html",
        products=products,
        category=category_obj,
        q=q,
        available=available,
        price_min=price_min,
        price_max=price_max,
        sort=sort,
        categories=Category.query.order_by(Category.id).all(),
    )


@bp.route("/<int:product_id>", methods=["GET", "POST"])
def detail(product_id):
    product = Product.query.get_or_404(product_id)
    form = ReviewForm()

    if current_user.is_authenticated:
        rv = RecentlyViewed.query.filter_by(userid=current_user.id, productid=product.id).first()
        if rv:
            rv.viewedat = datetime.utcnow()
        else:
            rv = RecentlyViewed(userid=current_user.id, productid=product.id)
            db.session.add(rv)
        db.session.commit()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Чтобы оставить отзыв, войдите в аккаунт.", "warning")
            return redirect(url_for("auth.login", next=request.path))

        review = Review(
            userid=current_user.id,
            productid=product.id,
            rating=int(form.rating.data),
            text=form.text.data,
            isapproved=False,
        )
        db.session.add(review)
        db.session.commit()
        flash("Ваш отзыв отправлен на модерацию.", "success")
        return redirect(url_for("catalog.detail", product_id=product.id))

    approved_reviews = (
        Review.query.filter_by(productid=product.id, isapproved=True)
        .order_by(Review.createdat.desc())
        .all()
    )

    return render_template(
        "catalog/detail.html",
        product=product,
        form=form,
        reviews=approved_reviews,
    )


@bp.route("/<int:product_id>/audio")
def product_audio(product_id):
    product = Product.query.get_or_404(product_id)

    if not product.audiodata:
        abort(404)

    response = Response(
        bytes(product.audiodata),
        mimetype=product.audiomime or "audio/mpeg",
    )
    response.headers["Accept-Ranges"] = "bytes"
    response.headers["Cache-Control"] = "public, max-age=3600"
    response.headers["Content-Length"] = str(len(product.audiodata))
    return response