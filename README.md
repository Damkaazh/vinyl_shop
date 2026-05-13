# Виниловая Гавань — учебный интернет-магазин (ВКР)

Магазин музыкальных инструментов, виниловых пластинок и проигрывателей. Винтажный стиль, двуязычный интерфейс RU/EN.

## Стек

- **Backend**: Python 3.11+, Flask 3, SQLAlchemy, Flask-Login, Flask-WTF, Flask-Mail
- **Frontend**: HTML5, CSS3 (Vintage palette), Vanilla JS
- **БД**: SQLite (по умолчанию). Поддерживает PostgreSQL/MS SQL через `DATABASE_URL`.
- **Email**: SMTP (Gmail/Mail.ru). При отсутствии SMTP — лог в `instance/emails.log`.

## Установка локально

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # отредактируйте при необходимости
python wsgi.py
```

Откройте http://localhost:5000

## Учётные записи

- **Администратор**: логин `admin`, пароль `admin12345` (`admin@vinylshop.local`)
- **Демо-пользователь**: логин `demo`, пароль `demo12345`

База инициализируется автоматически при первом запуске (см. `app/seed.py`).

## Структура

```
vinyl_shop/
├── app/
│   ├── __init__.py        # фабрика приложения, blueprints
│   ├── extensions.py      # db, login_manager, mail, migrate
│   ├── models.py          # 13 моделей: User, Product, Order, ...
│   ├── forms.py           # WTForms (валидация, дата >= 1940)
│   ├── i18n.py            # словари RU/EN
│   ├── utils.py           # save_upload, send_order_email, ...
│   ├── seed.py            # демо-данные
│   ├── routes/            # blueprints: main, auth, catalog, cart, account, admin, api
│   ├── templates/         # Jinja2-шаблоны
│   └── static/            # CSS, JS, изображения (SVG)
├── instance/              # БД SQLite, лог писем
├── scripts/generate_assets.py
├── config.py
├── wsgi.py                # точка входа (с middleware для пути /port/5000)
└── requirements.txt
```

## Возможности

- Регистрация, авторизация, личный кабинет с историей заказов и сеансов входа
- Каталог с фильтрами (наличие, акция, цена, рейтинг) и поиском с подсказками
- Карточка товара: галерея, характеристики, отзывы с модерацией
- Корзина, оформление заказа, отправка письма-подтверждения по SMTP
- Админ-панель: товары, новости, акции, модерация отзывов, заказы
- Двуязычный интерфейс RU/EN, тёмная тема, режим для слабовидящих
- Карта Яндекс в подвале (Уфа, ул. Ленина, 12)
- Кнопка «Подобрать новости по интересам» в корзине → внешние новости

## Деплой

Проект развёрнут на pplx.app. Для собственного хостинга:

```bash
gunicorn wsgi:app --bind 0.0.0.0:5000
```

При размещении за обратным прокси с префиксом установите переменную:

```bash
URL_PREFIX=/your-prefix gunicorn wsgi:app --bind 0.0.0.0:5000
```

## Автор

Дамир Ажманов · ВКР · 2026
