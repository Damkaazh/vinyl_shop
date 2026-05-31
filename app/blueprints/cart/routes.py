from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import current_user, login_required
from . import bp
from ...extensions import db
from ...models import CartItem, Product, Order, OrderItem, PromoCode
from ...forms import CheckoutForm, PromoApplyForm
from ...utils import send_order_email


PROMO_ERRORS = {
    "promo_not_found": "Промокод не найден.",
    "promo_inactive": "Промокод отключён.",
    "promo_expired": "Срок действия промокода истёк.",
    "promo_exhausted": "Лимит использований промокода исчерпан.",
    "promo_min_order": "Сумма заказа меньше минимальной для этого промокода.",
}


def _get_active_promo(order_total: float):
    """Возвращает (PromoCode, discount) из сессии, если всё в порядке.

    Если промокод стал невалидным (истёк, выключили, сумма упала) —
    выводит flash и снимает с сессии.
    """
    pid = session.get("promo_code_id")
    if not pid:
        return None, 0.0
    pc = PromoCode.query.get(pid)
    if not pc:
        session.pop("promo_code_id", None)
        return None, 0.0
    ok, reason = pc.is_valid(order_total)
    if not ok:
        session.pop("promo_code_id", None)
        flash(PROMO_ERRORS.get(reason, "Промокод больше не действует."), "warning")
        return None, 0.0
    return pc, pc.calc_discount(order_total)


@bp.route("/")
@login_required
def index():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    subtotal = sum(item.subtotal for item in items)
    promo, discount = _get_active_promo(subtotal)
    total = max(0.0, subtotal - discount)
    promo_form = PromoApplyForm()
    return render_template(
        "cart/index.html",
        items=items,
        subtotal=subtotal,
        total=total,
        promo=promo,
        discount=discount,
        promo_form=promo_form,
    )


@bp.route("/promo/apply", methods=["POST"])
@login_required
def promo_apply():
    form = PromoApplyForm()
    next_url = request.form.get("next") or url_for("cart.index")
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    subtotal = sum(item.subtotal for item in items)
    if not form.validate_on_submit():
        flash("Введите промокод.", "warning")
        return redirect(next_url)
    code = form.code.data.strip().upper()
    pc = PromoCode.query.filter_by(code=code).first()
    if not pc:
        flash(PROMO_ERRORS["promo_not_found"], "danger")
        return redirect(next_url)
    ok, reason = pc.is_valid(subtotal)
    if not ok:
        flash(PROMO_ERRORS.get(reason, "Промокод не подходит."), "danger")
        return redirect(next_url)
    session["promo_code_id"] = pc.id
    discount = pc.calc_discount(subtotal)
    flash(f"Промокод {pc.code} применён. Скидка: {discount:,.0f} ₽.".replace(",", "\u00a0"), "success")
    return redirect(next_url)


@bp.route("/promo/clear", methods=["POST"])
@login_required
def promo_clear():
    session.pop("promo_code_id", None)
    next_url = request.form.get("next") or url_for("cart.index")
    flash("Промокод убран.", "info")
    return redirect(next_url)


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
    subtotal = sum(item.subtotal for item in items)
    promo, discount = _get_active_promo(subtotal)
    total = max(0.0, subtotal - discount)
    form = CheckoutForm()
    promo_form = PromoApplyForm()
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
            discount=discount,
            promo_code=promo.code if promo else None,
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
        # инкремент счётчика промокода
        if promo:
            promo.used_count = (promo.used_count or 0) + 1
        # очищаем корзину
        for ci in items:
            db.session.delete(ci)
        db.session.commit()
        session.pop("promo_code_id", None)

        sent = send_order_email(order)
        if sent:
            flash("Заказ оформлен. Письмо с подтверждением отправлено на ваш e-mail.", "success")
        else:
            flash("Заказ оформлен. Подтверждение сохранено в журнал писем (instance/emails.log).", "success")
        return redirect(url_for("cart.success", order_id=order.id))
    return render_template(
        "cart/checkout.html",
        form=form,
        items=items,
        subtotal=subtotal,
        total=total,
        promo=promo,
        discount=discount,
        promo_form=promo_form,
    )


@bp.route("/success/<int:order_id>")
@login_required
def success(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template("cart/success.html", order=order)
