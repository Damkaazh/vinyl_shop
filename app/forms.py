"""Формы Flask-WTF с валидацией согласно требованиям ВКР."""
from datetime import date
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField,
    SelectField, DateField, TextAreaField, IntegerField, DecimalField,
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, Regexp, ValidationError, Optional, NumberRange,
)


def not_too_old(form, field):
    if field.data and field.data.year < 1940:
        raise ValidationError("Дата рождения не должна быть раньше 1940 года.")
    if field.data and field.data > date.today():
        raise ValidationError("Дата рождения не может быть в будущем.")


class RegistrationForm(FlaskForm):
    email = StringField("E-mail", validators=[
        DataRequired(message="Введите e-mail"),
        Email(message="Некорректный e-mail"),
        Length(max=120),
    ])
    login = StringField("Логин", validators=[
        DataRequired(message="Введите логин"),
        Length(min=3, max=64),
        Regexp(r"^[A-Za-z0-9_.-]+$", message="Только латиница, цифры и . _ -"),
    ])
    full_name = StringField("ФИО", validators=[
        DataRequired(message="Укажите ФИО"),
        Length(min=2, max=160),
    ])
    nickname = StringField("Никнейм", validators=[
        DataRequired(message="Укажите никнейм"),
        Length(min=2, max=64),
    ])
    birth_date = DateField("Дата рождения", validators=[DataRequired(message="Укажите дату рождения"), not_too_old])
    gender = SelectField("Пол", choices=[("male", "Мужской"), ("female", "Женский"), ("other", "Другое")],
                         validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[
        DataRequired(message="Введите пароль"),
        Length(min=6, max=128, message="Минимум 6 символов"),
    ])
    password2 = PasswordField("Повторите пароль", validators=[
        DataRequired(),
        EqualTo("password", message="Пароли не совпадают"),
    ])
    avatar = FileField("Аватар", validators=[
        Optional(),
        FileAllowed(["jpg", "jpeg", "png", "gif", "webp"], "Только изображения"),
    ])
    submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
    identifier = StringField("E-mail или логин", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class ForgotPasswordForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    submit = SubmitField("Восстановить")


class ReviewForm(FlaskForm):
    rating = SelectField("Оценка", choices=[(str(i), "★" * i) for i in range(5, 0, -1)],
                         validators=[DataRequired()])
    text = TextAreaField("Текст отзыва", validators=[DataRequired(), Length(min=5, max=2000)])
    submit = SubmitField("Отправить")


class CheckoutForm(FlaskForm):
    full_name = StringField("ФИО", validators=[DataRequired(), Length(max=160)])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    phone = StringField("Телефон", validators=[DataRequired(), Length(min=5, max=40)])
    address = StringField("Адрес", validators=[DataRequired(), Length(max=255)])
    delivery_method = SelectField("Способ получения", choices=[
        ("pickup", "Самовывоз"),
        ("courier", "Курьер"),
        ("post", "Почта России"),
    ], validators=[DataRequired()])
    payment_method = SelectField("Способ оплаты", choices=[
        ("card", "Картой онлайн"),
        ("cash", "Наличными при получении"),
        ("sbp", "СБП"),
    ], validators=[DataRequired()])
    comment = TextAreaField("Комментарий", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Подтвердить заказ")


class ProductForm(FlaskForm):
    category_id = SelectField("Категория", coerce=int, validators=[DataRequired()])
    name_ru = StringField("Название (RU)", validators=[DataRequired(), Length(max=200)])
    name_en = StringField("Name (EN)", validators=[DataRequired(), Length(max=200)])
    short_ru = StringField("Краткое описание (RU)", validators=[Optional(), Length(max=400)])
    short_en = StringField("Short (EN)", validators=[Optional(), Length(max=400)])
    description_ru = TextAreaField("Описание (RU)", validators=[Optional()])
    description_en = TextAreaField("Description (EN)", validators=[Optional()])
    specs_ru = TextAreaField("Характеристики (RU)", validators=[Optional()])
    specs_en = TextAreaField("Specs (EN)", validators=[Optional()])
    price = DecimalField("Цена, ₽", validators=[DataRequired(), NumberRange(min=0)])
    old_price = DecimalField("Старая цена", validators=[Optional(), NumberRange(min=0)])
    stock = IntegerField("Остаток", validators=[DataRequired(), NumberRange(min=0)])
    is_featured = BooleanField("Показывать на главной")
    image = FileField("Изображение", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "gif", "webp"])])
    submit = SubmitField("Сохранить")


class NewsForm(FlaskForm):
    title_ru = StringField("Заголовок (RU)", validators=[DataRequired(), Length(max=200)])
    title_en = StringField("Title (EN)", validators=[DataRequired(), Length(max=200)])
    body_ru = TextAreaField("Текст (RU)", validators=[DataRequired()])
    body_en = TextAreaField("Body (EN)", validators=[DataRequired()])
    image = FileField("Картинка", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "gif", "webp"])])
    is_featured = BooleanField("Показывать на главной")
    submit = SubmitField("Сохранить")


class PromotionForm(FlaskForm):
    title_ru = StringField("Заголовок (RU)", validators=[DataRequired(), Length(max=200)])
    title_en = StringField("Title (EN)", validators=[DataRequired(), Length(max=200)])
    body_ru = TextAreaField("Описание (RU)", validators=[DataRequired()])
    body_en = TextAreaField("Body (EN)", validators=[DataRequired()])
    discount_percent = IntegerField("Скидка, %", validators=[Optional(), NumberRange(min=0, max=100)])
    valid_until = DateField("Действует до", validators=[Optional()])
    image = FileField("Картинка", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "gif", "webp"])])
    submit = SubmitField("Сохранить")
