import os
import django

from pymongo import MongoClient


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hw_quotes.settings")
django.setup()

from quotes.models import Quote, Tag, Author    # noqa


# Налаштування підключення до MongoDB
mongo_client = MongoClient('mongodb+srv://ksushondrik369:48368463@dbgoitweb22.pcohoq9.mongodb.net/')
mongo_db = mongo_client.web22


# Функція для імпорту авторів
def import_authors():
    authors = mongo_db.authors.find()
    for author in authors:
        Author.objects.get_or_create(
            fullname=author['fullname'],
            born_date=author['born_date'],
            born_location=author['born_location'],
            description=author['description']
        )


# Функція для імпорту цитат
def import_quotes():
    quotes = mongo_db.quotes.find()
    for quote in quotes:
        tags = []
        for tag in quote['tags']:
            t, *_ = Tag.objects.get_or_create(name=tag)
            tags.append(t)

        # Перевірка чи існує цитата
        exist_quote = Quote.objects.filter(quote=quote['quote']).exists()

        if not exist_quote:
            # Знаходимо автора за fullname
            author_data = mongo_db.authors.find_one({'_id': quote['author']})
            author = Author.objects.get(fullname=author_data['fullname'])
            # Створення цитати
            q = Quote.objects.create(
                quote=quote['quote'],
                author=author,
            )
            # Додавання тегів до цитати
            for tag in tags:
                q.tags.add(tag)


# Запуск імпорту
import_authors()
import_quotes()
