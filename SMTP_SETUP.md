# Настройка SMTP для писем «Виниловой Гавани»

Сейчас если SMTP не настроен — все письма (приветственное, заказ, вход) **записываются в файл** `instance/emails.log` вместо реальной отправки. Это удобно для разработки и защиты ВКР: «вот лог писем, всё работает».

Чтобы письма реально уходили на e-mail, задайте переменные окружения.

## Что отправляется

| Когда | Шаблон | Тема |
|-------|--------|------|
| Регистрация нового пользователя | `welcome.html` / `.txt` | Добро пожаловать в «Виниловую Гавань» |
| Оформление заказа | `order_confirmation.html` / `.txt` | Заказ №N в магазине «Виниловая Гавань» |
| Вход в аккаунт | `login_alert.html` / `.txt` | Вход в аккаунт «Виниловая Гавань» |

Если SMTP падает с ошибкой — письмо тоже уйдёт в `emails.log`, регистрация/вход/заказ при этом не сломаются (отправка обёрнута в try/except).

## Общие переменные окружения

| Ключ | Назначение |
|------|------------|
| `MAIL_SERVER` | Хост SMTP |
| `MAIL_PORT` | Порт (обычно 587 для STARTTLS или 465 для SSL) |
| `MAIL_USE_TLS` | `1` для STARTTLS (порт 587) |
| `MAIL_USE_SSL` | `1` для SSL (порт 465). Не включать одновременно с TLS |
| `MAIL_USERNAME` | Логин SMTP (обычно полный e-mail) |
| `MAIL_PASSWORD` | Пароль (или App Password — см. ниже) |
| `MAIL_DEFAULT_SENDER` | От кого идут письма, напр. `Виниловая Гавань <noreply@example.com>` |
| `MAIL_SUPPRESS_SEND` | `1` — принудительно писать только в лог, не отправлять |

## Примеры провайдеров

### Gmail (нужен App Password)

1. Включите 2FA в Google-аккаунте.
2. Создайте App Password: <https://myaccount.google.com/apppasswords> → выберите «Mail» → скопируйте 16-значный пароль.
3. Переменные:

```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USE_SSL=0
MAIL_USERNAME=your.address@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx     # App Password, не основной пароль
MAIL_DEFAULT_SENDER=your.address@gmail.com
```

### Яндекс.Почта

1. В настройках Яндекс.Почты: «Все настройки» → «Почтовые программы» → включите доступ по IMAP/SMTP.
2. Создайте «Пароль приложения» в Яндекс ID.
3. Переменные:

```
MAIL_SERVER=smtp.yandex.ru
MAIL_PORT=465
MAIL_USE_TLS=0
MAIL_USE_SSL=1
MAIL_USERNAME=your.address@yandex.ru
MAIL_PASSWORD=app_password_from_yandex_id
MAIL_DEFAULT_SENDER=your.address@yandex.ru
```

### Mail.ru

1. В настройках Mail.ru: «Безопасность» → «Пароли для внешних приложений» → создайте.
2. Переменные:

```
MAIL_SERVER=smtp.mail.ru
MAIL_PORT=465
MAIL_USE_TLS=0
MAIL_USE_SSL=1
MAIL_USERNAME=your.address@mail.ru
MAIL_PASSWORD=external_app_password
MAIL_DEFAULT_SENDER=your.address@mail.ru
```

## Где задавать переменные

### Локально (Windows PowerShell)

В корне проекта создайте файл `.env`:

```
MAIL_SERVER=smtp.yandex.ru
MAIL_PORT=465
MAIL_USE_SSL=1
MAIL_USERNAME=...
MAIL_PASSWORD=...
MAIL_DEFAULT_SENDER=...
```

`config.py` уже подхватывает `.env` через `python-dotenv`.

### На Render

Web Service → **Environment** → Add Environment Variable. Добавьте каждую переменную из списка выше отдельной строкой. После сохранения Render автоматически перезапустит сервис.

## Промокоды

Промокоды создаются в админке: `/admin/promocodes` → «+ Новый».

Поля:
- **Код** — латиница/цифры/`-`/`_`, например `WELCOME10`.
- **Тип скидки** — `%` (процент от суммы) или `₽` (фиксированная сумма).
- **Размер скидки** — число.
- **Мин. сумма заказа** — `0` = без ограничений.
- **Лимит использований** — `0` = бесконечный.
- **Действует до** — пусто = бессрочно.
- **Активен** — галочка для быстрого включения/выключения.

При оформлении заказа промокод вводится в поле в корзине или на странице оформления. Скидка фиксируется в `Order.discount` и `Order.promo_code`, счётчик `used_count` инкрементируется.

## Команды для пуша

```powershell
git add app/ SMTP_SETUP.md
git commit -m "Patch 4: promo codes + Flask-Mail (welcome / order / login emails)"
git push origin main
```
