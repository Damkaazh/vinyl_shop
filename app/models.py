"""Модели базы данных.

Схема:
    User              — пользователи (с ролью admin/user) + аватар + ФИО, никнейм, дата рождения, пол
    LoginSession      — журнал входов (предыдущие сеансы)
    Category          — категории (instruments / vinyl / players)
    Product           — товары
    ProductImage      — дополнительные фото товара
    Review            — отзывы (с модерацией)
    Order / OrderItem — заказы и позиции
    Favorite          — избранные новости/товары пользователя
    News              — новости / статьи
    Promotion         — акции
    CartItem          — корзина (для авторизованных)
    RecentlyViewed    — последние просмотры
"""
from datetime import datetime, date
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    login = db.Column(db.String(64), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(160), nullable=False)
    nickname = db.Column(db.String(64), unique=True, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(8), nullable=False)  # 'male' / 'female' / 'other'
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), default="default-avatar.svg")
    role = db.Column(db.String(16), default="user", nullable=False)  # 'user' / 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sessions = db.relationship("LoginSession", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    orders = db.relationship("Order", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    favorites = db.relationship("Favorite", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    cart_items = db.relationship("CartItem", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    recently_viewed = db.relationship("RecentlyViewed", backref="user", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class LoginSession(db.Model):
    __tablename__ = "login_sessions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(64), unique=True, nullable=False)
    name_ru = db.Column(db.String(120), nullable=False)
    name_en = db.Column(db.String(120), nullable=False)
    description_ru = db.Column(db.Text, default="")
    description_en = db.Column(db.Text, default="")

    products = db.relationship("Product", backref="category", lazy="dynamic")

    def name(self, lang="ru"):
        return self.name_en if lang == "en" else self.name_ru


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False, index=True)
    name_ru = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=False)
    short_ru = db.Column(db.String(400), default="")
    short_en = db.Column(db.String(400), default="")
    description_ru = db.Column(db.Text, default="")
    description_en = db.Column(db.Text, default="")
    specs_ru = db.Column(db.Text, default="")  # характеристики, по строке "ключ: значение"
    specs_en = db.Column(db.Text, default="")
    price = db.Column(db.Numeric(10, 2), nullable=False)
    old_price = db.Column(db.Numeric(10, 2))  # для акций
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255), default="placeholder.svg")
    is_featured = db.Column(db.Boolean, default=False)  # для слайдера
    # Аудио-превью. Критично: deferred — блоб не грузится при обычном SELECT,
    # только при явном обращении к product.audio_data. Без этого любой листинг каталога тянет в RAM
    # все аудиофайлы → OOM на Render free (512 МБ).
    audio_data = orm.deferred(db.Column(db.LargeBinary, nullable=True))
    audio_mime = db.Column(db.String(64), nullable=True)   # например audio/mpeg, audio/ogg
    audio_name = db.Column(db.String(255), nullable=True)  # исходное имя файла
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def has_audio(self):
        # Не дёргаем блоб — смотрим по лёгким колонкам. audio_name всегда заполняется вместе с audio_data.
        return bool(self.audio_name) or bool(self.audio_mime)

    images = db.relationship("ProductImage", backref="product", lazy="dynamic", cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="product", lazy="dynamic", cascade="all, delete-orphan")

    def name(self, lang="ru"):
        return self.name_en if lang == "en" else self.name_ru

    def short(self, lang="ru"):
        return self.short_en if lang == "en" else self.short_ru

    def description(self, lang="ru"):
        return self.description_en if lang == "en" else self.description_ru

    def specs(self, lang="ru"):
        return self.specs_en if lang == "en" else self.specs_ru

    @property
    def in_stock(self):
        return (self.stock or 0) > 0

    @property
    def avg_rating(self):
        approved = [r.rating for r in self.reviews if r.is_approved]
        return round(sum(approved) / len(approved), 1) if approved else 0

    @property
    def reviews_count(self):
        return sum(1 for r in self.reviews if r.is_approved)


class ProductImage(db.Model):
    __tablename__ = "product_images"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    image = db.Column(db.String(255), nullable=False)


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=False)  # модерация
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    full_name = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(40), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    delivery_method = db.Column(db.String(40), default="pickup")  # pickup / courier / post
    payment_method = db.Column(db.String(40), default="cash")  # cash / sbp (картой онлайн отключена)
    comment = db.Column(db.Text, default="")
    total = db.Column(db.Numeric(10, 2), nullable=False)
    discount = db.Column(db.Numeric(10, 2), default=0)
    promo_code = db.Column(db.String(64))
    status = db.Column(db.String(40), default="new")  # new / paid / shipped / done / canceled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", lazy="joined", cascade="all, delete-orphan")

    @property
    def subtotal(self):
        """Сумма до скидки."""
        return float(self.total) + float(self.discount or 0)


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    product = db.relationship("Product")

    @property
    def subtotal(self):
        return float(self.price) * self.quantity


class Favorite(db.Model):
    """Избранное: либо новость, либо товар."""
    __tablename__ = "favorites"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    news_id = db.Column(db.Integer, db.ForeignKey("news.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product")
    news = db.relationship("News")


class News(db.Model):
    __tablename__ = "news"
    id = db.Column(db.Integer, primary_key=True)
    title_ru = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    body_ru = db.Column(db.Text, nullable=False)
    body_en = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), default="news-default.svg")
    rating = db.Column(db.Integer, default=0)  # сумма оценок
    rating_count = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)

    def title(self, lang="ru"):
        return self.title_en if lang == "en" else self.title_ru

    def body(self, lang="ru"):
        return self.body_en if lang == "en" else self.body_ru

    @property
    def avg_rating(self):
        return round(self.rating / self.rating_count, 1) if self.rating_count else 0


class Promotion(db.Model):
    __tablename__ = "promotions"
    id = db.Column(db.Integer, primary_key=True)
    title_ru = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    body_ru = db.Column(db.Text, nullable=False)
    body_en = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), default="promo-default.svg")
    discount_percent = db.Column(db.Integer, default=0)
    valid_until = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def title(self, lang="ru"):
        return self.title_en if lang == "en" else self.title_ru

    def body(self, lang="ru"):
        return self.body_en if lang == "en" else self.body_ru


class PromoCode(db.Model):
    """Промокод с фиксированной (₽) или процентной скидкой."""
    __tablename__ = "promo_codes"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    discount_type = db.Column(db.String(16), default="percent")  # 'percent' | 'fixed'
    discount_value = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    min_order = db.Column(db.Numeric(10, 2), default=0)
    usage_limit = db.Column(db.Integer, default=0)  # 0 = без лимита
    used_count = db.Column(db.Integer, default=0)
    valid_until = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_valid(self, order_total: float) -> tuple[bool, str]:
        """Проверяет валидность промокода для заказа. Возвращает (ok, причина-ключ)."""
        if not self.is_active:
            return False, "promo_inactive"
        if self.valid_until and self.valid_until < date.today():
            return False, "promo_expired"
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False, "promo_exhausted"
        if self.min_order and float(order_total) < float(self.min_order):
            return False, "promo_min_order"
        return True, "ok"

    def calc_discount(self, order_total: float) -> float:
        """Считает размер скидки в ₽ (не больше суммы заказа)."""
        if self.discount_type == "percent":
            d = float(order_total) * float(self.discount_value) / 100.0
        else:
            d = float(self.discount_value)
        return min(round(d, 2), float(order_total))


class CartItem(db.Model):
    __tablename__ = "cart_items"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product")

    @property
    def subtotal(self):
        return float(self.product.price) * self.quantity


class RecentlyViewed(db.Model):
    __tablename__ = "recently_viewed"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product")
