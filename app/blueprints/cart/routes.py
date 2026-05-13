from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from . import bp
from ...extensions import db
from ...models import CartItem, Product, Order, OrderItem
from ...forms import CheckoutForm
from ...utils import send_order_email


@bp.route("/")
@login_required
def index():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.subtotal for item in items)
    return render_template("cart/index.html", items=items, total=total)


@bp.route("/add/<int:product_id>", methods=["POST"])
@login_required
def add(product_id):
    product = Product.query.get_or_404(product_id)
    qty = int(request.form.get("quantity", 1))
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    if item:
        item.quantity += qty
    else:
        item = CartItem(user_id=current_user.id, product_id=product.id, quantity=qty)
        db.session.add(item)
    db.session.commit()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        count = sum(i.quantity for i in CartItem.query.filter_by(user_id=current_user.id).all())
        return jsonify({"ok": True, "count": count})
    flash("Товар добавлен в корзину.", "success")
    return redirect(request.referrer or url_for("catalog.index"))


@bp.route("/remove/<int:item_id>", methods=["POST"])
@login_required
def remove(item_id):
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash("Товар удалён из корзины.", "info")
    return redirect(url_for("cart.index"))


@bp.route("/update/<int:item_id>", methods=["POST"])
@login_required
def update(item_id):
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    qty = max(1, int(request.form.get("quantity", 1)))
    item.quantity = qty
    db.session.commit()
    return redirect(url_for("cart.index"))


@bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash("Корзина пуста.", "warning")
        return redirect(url_for("cart.index"))
    total = sum(item.subtotal for item in items)
    form = CheckoutForm()
    if request.method == "GET":
        form.full_name.data = current_user.full_name
        form.email.data = current_user.email
    if form.validate_on_submit():
        order = Order(
            user_id=current_user.id,
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            delivery_method=form.delivery_method.data,
            payment_method=form.payment_method.data,
            comment=form.comment.data or "",
            total=total,
        )
        db.session.add(order)
        db.session.flush()
        for ci in items:
            db.session.add(OrderItem(
                order_id=order.id,
                product_id=ci.product_id,
                name=ci.product.name_ru,
                price=ci.product.price,
                quantity=ci.quantity,
            ))
        # очищаем корзину
        for ci in items:
            db.session.delete(ci)
        db.session.commit()

        sent = send_order_email(order)
        if sent:
            flash("Заказ оформлен. Письмо с подтверждением отправлено на ваш e-mail.", "success")
        else:
            flash("Заказ оформлен. Подтверждение сохранено в журнал писем (instance/emails.log).", "success")
        return redirect(url_for("cart.success", order_id=order.id))
    return render_template("cart/checkout.html", form=form, items=items, total=total)


@bp.route("/success/<int:order_id>")
@login_required
def success(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template("cart/success.html", order=order)
