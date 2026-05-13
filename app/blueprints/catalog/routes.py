from flask import render_template, request, redirect, url_for, flash, abort, g
from flask_login import current_user, login_required
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
    category = None
    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first_or_404()
        query = query.filter(Product.category_id == category.id)

    # Фильтры
    q = request.args.get("q", "").strip()
    available = request.args.get("available")
    price_min = request.args.get("price_min", type=float)
    price_max = request.args.get("price_max", type=float)
    sort = request.args.get("sort", "new")

    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            Product.name_ru.ilike(like), Product.name_en.ilike(like),
            Product.description_ru.ilike(like), Product.description_en.ilike(like),
        ))
    if available:
        query = query.filter(Product.stock > 0)
    if price_min is not None:
        query = query.filter(Product.price >= price_min)
    if price_max is not None:
        query = query.filter(Product.price <= price_max)

    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort == "rating":
        # сортировка по среднему рейтингу делается на стороне Python (для простоты)
        products = query.all()
        products.sort(key=lambda p: p.avg_rating, reverse=True)
        return render_template(
            "catalog/list.html", products=products, category=category,
            q=q, available=available, price_min=price_min, price_max=price_max, sort=sort,
            categories=Category.query.order_by(Category.id).all(),
        )
    else:
        query = query.order_by(Product.created_at.desc())

    products = query.all()
    return render_template(
        "catalog/list.html", products=products, category=category,
        q=q, available=available, price_min=price_min, price_max=price_max, sort=sort,
        categories=Category.query.order_by(Category.id).all(),
    )


@bp.route("/<int:product_id>", methods=["GET", "POST"])
def detail(product_id):
    product = Product.query.get_or_404(product_id)
    form = ReviewForm()

    # сохранение в "недавно просмотренные"
    if current_user.is_authenticated:
        rv = RecentlyViewed.query.filter_by(user_id=current_user.id, product_id=product.id).first()
        if rv:
            from datetime import datetime
            rv.viewed_at = datetime.utcnow()
        else:
            rv = RecentlyViewed(user_id=current_user.id, product_id=product.id)
            db.session.add(rv)
        db.session.commit()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Чтобы оставить отзыв, войдите в аккаунт.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        review = Review(
            user_id=current_user.id,
            product_id=product.id,
            rating=int(form.rating.data),
            text=form.text.data,
            is_approved=False,  # модерация
        )
        db.session.add(review)
        db.session.commit()
        flash("Ваш отзыв отправлен на модерацию.", "success")
        return redirect(url_for("catalog.detail", product_id=product.id))

    approved_reviews = Review.query.filter_by(product_id=product.id, is_approved=True).order_by(Review.created_at.desc()).all()
    return render_template("catalog/detail.html", product=product, form=form, reviews=approved_reviews)
