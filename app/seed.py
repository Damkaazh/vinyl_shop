"""Заполнение базы демо-данными при первом запуске."""
from datetime import date, datetime, timedelta
from flask import current_app
from .extensions import db
from .models import User, Category, Product, News, Promotion


def seed_if_empty():
    if User.query.first() is not None:
        return  # уже есть данные

    # Админ
    admin = User(
        email=current_app.config["ADMIN_EMAIL"],
        login="admin",
        full_name="Администратор Магазина",
        nickname="root",
        birth_date=date(1990, 1, 1),
        gender="other",
        role="admin",
        avatar="default-avatar.svg",
    )
    admin.set_password(current_app.config["ADMIN_PASSWORD"])
    db.session.add(admin)

    # Демо-пользователь
    demo = User(
        email="user@vinylshop.local",
        login="demo",
        full_name="Иван Петров",
        nickname="vinyl_lover",
        birth_date=date(1995, 5, 20),
        gender="male",
        role="user",
        avatar="default-avatar.svg",
    )
    demo.set_password("demo12345")
    db.session.add(demo)

    # Категории
    cats = [
        Category(slug="instruments", name_ru="Музыкальные инструменты", name_en="Musical Instruments",
                 description_ru="Гитары, клавишные, духовые и редкие винтажные инструменты.",
                 description_en="Guitars, keyboards, brass and rare vintage instruments."),
        Category(slug="vinyl", name_ru="Виниловые пластинки", name_en="Vinyl Records",
                 description_ru="Лимитированные издания, классика рока, джаз и саундтреки.",
                 description_en="Limited editions, classic rock, jazz and soundtracks."),
        Category(slug="players", name_ru="Проигрыватели", name_en="Turntables",
                 description_ru="Винтажные проигрыватели, новые HiFi-модели и аксессуары.",
                 description_en="Vintage turntables, modern HiFi units and accessories."),
    ]
    for c in cats:
        db.session.add(c)
    db.session.flush()

    cat_inst, cat_vinyl, cat_players = cats

    # Товары
    products = [
        # Инструменты
        Product(category_id=cat_inst.id,
                name_ru="Гитара Fender Stratocaster '62", name_en="Fender Stratocaster '62 Guitar",
                short_ru="Винтажная электрогитара с тёплым звуком", short_en="Vintage electric guitar with warm tone",
                description_ru="Реплика легендарной модели 1962 года: ольховый корпус, кленовый гриф, три сингла. Идеально для блюза и рока.",
                description_en="Replica of the legendary 1962 model: alder body, maple neck, three single coils. Perfect for blues and rock.",
                specs_ru="Корпус: ольха\nГриф: клён\nДатчики: 3 single-coil\nРодина: USA",
                specs_en="Body: alder\nNeck: maple\nPickups: 3 single-coil\nOrigin: USA",
                price=89900, old_price=99900, stock=4, is_featured=True, image="product-guitar.svg"),
        Product(category_id=cat_inst.id,
                name_ru="Пианино Yamaha U1", name_en="Yamaha U1 Upright Piano",
                short_ru="Акустическое пианино студийного класса", short_en="Studio-grade upright piano",
                description_ru="Лучшее акустическое пианино в своём классе. Глубокий звук, надёжный механизм.",
                description_en="Best-in-class acoustic upright. Deep sound and reliable action.",
                specs_ru="Высота: 121 см\nКлавиш: 88\nПедалей: 3",
                specs_en="Height: 121 cm\nKeys: 88\nPedals: 3",
                price=420000, stock=2, is_featured=True, image="product-piano.svg"),
        Product(category_id=cat_inst.id,
                name_ru="Саксофон Selmer Mark VI", name_en="Selmer Mark VI Saxophone",
                short_ru="Легендарный альт-саксофон", short_en="Legendary alto saxophone",
                description_ru="Эталонный инструмент джазовых музыкантов 60-х. Тёплый, певучий тон.",
                description_en="Reference instrument of 1960s jazz. Warm singing tone.",
                specs_ru="Тип: альт\nГод: 1965\nСостояние: восстановлен",
                specs_en="Type: alto\nYear: 1965\nCondition: restored",
                price=540000, stock=1, is_featured=False, image="product-sax.svg"),
        # Винил
        Product(category_id=cat_vinyl.id,
                name_ru="Pink Floyd — The Dark Side of the Moon (LP)", name_en="Pink Floyd — The Dark Side of the Moon (LP)",
                short_ru="Юбилейное переиздание 50-летия", short_en="50th anniversary remaster",
                description_ru="Свежий ремастер на тяжёлом 180-граммовом виниле. Гейтфолд-конверт, оригинальные постеры.",
                description_en="Fresh remaster on 180-gram heavy vinyl. Gatefold sleeve, original posters.",
                specs_ru="Год: 2023\nМасса: 180 г\nЛейбл: Pink Floyd Records",
                specs_en="Year: 2023\nWeight: 180 g\nLabel: Pink Floyd Records",
                price=4990, stock=18, is_featured=True, image="product-vinyl-pf.svg"),
        Product(category_id=cat_vinyl.id,
                name_ru="Miles Davis — Kind of Blue (LP)", name_en="Miles Davis — Kind of Blue (LP)",
                short_ru="Эталон модального джаза", short_en="The benchmark of modal jazz",
                description_ru="Mono-mix на 180-граммовом виниле. Подлинный звук эпохи 1959 года.",
                description_en="Mono mix on 180g vinyl. Authentic 1959 sound.",
                specs_ru="Год: 2022\nМасса: 180 г\nLабель: Columbia",
                specs_en="Year: 2022\nWeight: 180 g\nLabel: Columbia",
                price=3990, stock=22, is_featured=True, image="product-vinyl-miles.svg"),
        Product(category_id=cat_vinyl.id,
                name_ru="The Beatles — Abbey Road (LP)", name_en="The Beatles — Abbey Road (LP)",
                short_ru="Стерео-ремикс 2019", short_en="2019 stereo remix",
                description_ru="Праздничное переиздание к 50-летию альбома, стерео-ремикс Джайлса Мартина.",
                description_en="50th anniversary release with Giles Martin's stereo remix.",
                specs_ru="Год: 2019\nМасса: 180 г\nЛейбл: Apple",
                specs_en="Year: 2019\nWeight: 180 g\nLabel: Apple",
                price=4490, stock=14, image="product-vinyl-beatles.svg"),
        # Проигрыватели
        Product(category_id=cat_players.id,
                name_ru="Technics SL-1200 MK7", name_en="Technics SL-1200 MK7",
                short_ru="Профессиональный DJ-проигрыватель", short_en="Pro DJ turntable",
                description_ru="Прямой привод, кварцевая стабилизация, классический алюминиевый корпус.",
                description_en="Direct drive, quartz stabilization, classic aluminium chassis.",
                specs_ru="Привод: прямой\nСкорости: 33/45/78\nКорпус: алюминий",
                specs_en="Drive: direct\nSpeeds: 33/45/78\nChassis: aluminium",
                price=119900, stock=6, is_featured=True, image="product-player-technics.svg"),
        Product(category_id=cat_players.id,
                name_ru="Pro-Ject Debut Carbon EVO", name_en="Pro-Ject Debut Carbon EVO",
                short_ru="HiFi-проигрыватель для дома", short_en="Home HiFi turntable",
                description_ru="Карбоновый тонарм, картридж Ortofon 2M Red, изящный корпус.",
                description_en="Carbon tonearm, Ortofon 2M Red cartridge, elegant body.",
                specs_ru="Привод: пассик\nКартридж: Ortofon 2M Red\nЦвет: матовый чёрный",
                specs_en="Drive: belt\nCartridge: Ortofon 2M Red\nColor: matte black",
                price=64900, stock=10, is_featured=True, image="product-player-projekt.svg"),
        Product(category_id=cat_players.id,
                name_ru="Винтажный Rega Planar 3 (1980)", name_en="Vintage Rega Planar 3 (1980)",
                short_ru="Восстановленный британский классик", short_en="Restored British classic",
                description_ru="Полностью обслужен, новый картридж, оригинальная пыльник-крышка.",
                description_en="Fully serviced, new cartridge, original dust cover.",
                specs_ru="Год: 1980\nСостояние: отличное\nКартридж: новый",
                specs_en="Year: 1980\nCondition: excellent\nCartridge: new",
                price=85000, stock=1, image="product-player-rega.svg"),
    ]
    for p in products:
        db.session.add(p)

    # Новости
    news_items = [
        News(title_ru="Привезли редкие японские пластинки 70-х",
             title_en="Rare 1970s Japanese pressings have arrived",
             body_ru="В наш магазин поступила партия японских прессингов 1970-х: Yellow Magic Orchestra, Haruomi Hosono, Casiopea и другие. Пластинки в коллекционном состоянии.",
             body_en="A new batch of 1970s Japanese pressings has arrived: YMO, Haruomi Hosono, Casiopea and more. All in collectible condition.",
             rating=42, rating_count=12, is_featured=True, image="news-japan.svg"),
        News(title_ru="Открыли мастерскую по реставрации проигрывателей",
             title_en="We opened a turntable restoration workshop",
             body_ru="Теперь ваши винтажные вертушки получат вторую жизнь у наших мастеров: замена пассиков, юстировка тонармов, ультразвуковая чистка.",
             body_en="Your vintage decks now get a second life with our craftsmen: belt replacement, tonearm setup, ultrasonic cleaning.",
             rating=28, rating_count=9, is_featured=True, image="news-workshop.svg"),
        News(title_ru="Гид по жанрам: с чего начать коллекцию джаза",
             title_en="Genre guide: where to start a jazz collection",
             body_ru="Подобрали 10 пластинок, без которых не обходится ни одна джазовая коллекция: от Майлза Дэвиса до Билла Эванса.",
             body_en="We picked 10 records that every jazz collection needs: from Miles Davis to Bill Evans.",
             rating=51, rating_count=14, is_featured=True, image="news-jazz.svg"),
        News(title_ru="Новая поставка винтажных гитар Fender и Gibson",
             title_en="Fresh batch of vintage Fender and Gibson guitars",
             body_ru="Поступление редких моделей 60-70-х годов. Все инструменты прошли мастерскую проверку.",
             body_en="A delivery of rare 1960s-70s models. All have passed our master's inspection.",
             rating=35, rating_count=10, image="news-guitars.svg"),
    ]
    for n in news_items:
        db.session.add(n)

    # Акции
    promos = [
        Promotion(title_ru="-15% на все пластинки джаза",
                  title_en="-15% off all jazz vinyl",
                  body_ru="До конца месяца — скидка 15% на весь джазовый раздел. Промокод не нужен.",
                  body_en="Until end of month — 15% off the entire jazz section. No promo code needed.",
                  discount_percent=15, valid_until=date.today() + timedelta(days=20),
                  image="promo-jazz.svg"),
        Promotion(title_ru="Игла в подарок при покупке проигрывателя",
                  title_en="Free cartridge with any turntable",
                  body_ru="Купите любой проигрыватель из каталога — игла Ortofon в подарок.",
                  body_en="Buy any turntable from the catalog and get an Ortofon cartridge free.",
                  discount_percent=0, valid_until=date.today() + timedelta(days=30),
                  image="promo-needle.svg"),
    ]
    for pr in promos:
        db.session.add(pr)

    db.session.commit()
    current_app.logger.info("Database seeded with demo data.")
