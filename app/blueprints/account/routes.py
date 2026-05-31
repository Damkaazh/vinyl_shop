from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from . import bp
from ...extensions import db
from ...models import Order, Favorite, RecentlyViewed, LoginSession


@bp.route("/")
@login_required
def index():
    orders = Order.query.filter_by(userid=current_user.id).order_by(Order.createdat.desc()).all()
    current_order = next((o for o in orders if o.status in ("new", "paid", "shipped")), None)

    favorites = Favorite.query.filter_by(userid=current_user.id).order_by(Favorite.createdat.desc()).all()

    recent = (
        RecentlyViewed.query.filter_by(userid=current_user.id)
        .order_by(RecentlyViewed.viewedat.desc())
        .limit(8)
        .all()
    )

    sessions = (
        LoginSession.query.filter_by(userid=current_user.id)
        .order_by(LoginSession.loggedat.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "account/index.html",
        orders=orders,
        current_order=current_order,
        favorites=favorites,
        recent=recent,
        sessions=sessions,
    )


@bp.route("/favorites/toggle", methods=["POST"])
@login_required
def toggle_favorite():
    product_id = request.form.get("product_id", type=int)
    news_id = request.form.get("news_id", type=int)

    if product_id:
        fav = Favorite.query.filter_by(userid=current_user.id, productid=product_id).first()
        if fav:
            db.session.delete(fav)
        else:
            db.session.add(Favorite(userid=current_user.id, productid=product_id))

    elif news_id:
        fav = Favorite.query.filter_by(userid=current_user.id, newsid=news_id).first()
        if fav:
            db.session.delete(fav)
        else:
            db.session.add(Favorite(userid=current_user.id, newsid=news_id))

    db.session.commit()
    return redirect(request.referrer or url_for("account.index"))