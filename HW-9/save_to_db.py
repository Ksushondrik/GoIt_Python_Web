import json

from datetime import datetime

from mongoengine import connect, Document, StringField, ListField, DateTimeField, ReferenceField, CASCADE

connect(db="web22",
        host="mongodb+srv://ksushondrik369:48368463@dbgoitweb22.pcohoq9.mongodb.net/?retryWrites=true&w=majority&appName=DBGoITWeb22")


class Author(Document):
    fullname = StringField(max_length=50, required=True)
    born_date = DateTimeField(required=True)
    born_location = StringField(max_length=150)
    description = StringField()
    meta = {'collection': 'authors'}


class Quote(Document):
    tags = ListField(StringField(max_length=200))
    author = ReferenceField(Author, reverse_delete_rule=CASCADE)
    quote = StringField(required=True)
    meta = {'collection': 'quotes'}


def create_author(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        authors = json.load(file)
        for aut in authors:
            existing_author = Author.objects(fullname=aut["fullname"]).first()
            if not existing_author:
                born_date = datetime.strptime(aut["born_date"], "%B %d, %Y")
                author = Author(
                    fullname=aut["fullname"],
                    born_date=born_date,
                    born_location=aut.get("born_location", ""),
                    description=aut.get("description", "")
                )
                author.save()
            else:
                print(f"Author {aut['fullname']} already exists")
                continue


def create_quote(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        quotes = json.load(f)
        for quo in quotes:
            name_a = quo["author"]
            author = Author.objects(fullname=name_a).first()
            existing_quote = Quote.objects(quote=quo["quote"]).first()
            if not existing_quote:
                quote = Quote(
                    tags=quo.get("tags", ""),
                    author=author,
                    quote=quo["quote"]
                )
                quote.save()
            else:
                print(f"Quote already exists")
                continue


def read_name(name):
    author = Author.objects(fullname=name).first()
    if author:
        quotes = Quote.objects(author=author).all()
        if quotes:
            result = [quote.quote for quote in quotes]
            return f"Quotes by '{author}': {','.join(result)}"
        else:
            return f"No quotes found by '{author}'."
    else:
        return f"Author {name} not found"


def read_tag(tag):
    quotes = Quote.objects(tags=tag).all()
    if quotes:
        result = []
        for quote in quotes:
            result.append(quote.quote)
        return f"Quotes with tag '{tag}': {result}"
    else:
        return f"No quotes found with tag '{tag}'."


def read_tags(tags):
    tags_list = tags.split(',')
    quotes = Quote.objects(tags__in=tags_list).all()
    if quotes:
        result = [quote.quote for quote in quotes]
        return f"Quotes with tags '{tags}': {', '.join(result)}"
    else:
        return f"No quotes found with tags '{', '.join(tags)}'."


def main():
    while True:
        cmd = input('Enter the action in "command:value" format: ')
        if ':' in cmd:
            action, value = cmd.split(':', 1)
            match action:
                case 'name':
                    print(read_name(value))
                case 'tag':
                    print(read_tag(value))
                case 'tags':
                    print(read_tags(value))
                case _:
                    print('Unknown command')
        elif cmd == 'exit':
            print("Exiting...")
            break
        else:
            print('Invalid command format. Please enter in "command:value" format.')


if __name__ == '__main__':
    create_author('authors.json')
    create_quote('quotes.json')
    main()
