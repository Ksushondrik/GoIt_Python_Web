from random import randint

import pika
from faker import Faker
from mongoengine import connect, Document, StringField, BooleanField, DateTimeField

connect(db="web22",
        host="mongodb+srv://ksushondrik369:48368463@dbgoitweb22.pcohoq9.mongodb.net/?retryWrites=true&w=majority&appName=DBGoITWeb22")

credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange='HW_8', exchange_type='fanout', durable=True)
channel.queue_declare(queue='mail_queue', durable=True)
channel.queue_bind(exchange="HW_8", queue="mail_queue")

fake = Faker('uk-UA')


class Contact(Document):
    fullname = StringField(max_length=50, required=True)
    email = StringField(max_length=50, required=True)
    phone = StringField(max_length=20)
    address = StringField(max_length=200)
    birthday = DateTimeField()
    sent = BooleanField(default=False, required=True)


def create_contacts(quantity: int):
    contacts = []
    for con in range(quantity):
        contact = Contact(
            fullname=fake.name(),
            email=fake.email(),
            phone=fake.phone_number(),
            address=fake.address(),
            birthday=fake.date_of_birth(),
        )
        contact.save()
        contacts.append(contact)
    return contacts


def sending_email(contacts: list):
    ids = [str(contact.id) for contact in contacts]
    count = 0
    for i in ids:
        channel.basic_publish(exchange="HW_8", routing_key="", body=i)
        print(f"[x] Sent {i}")
        count += 1
    print(f"[x] {count} contacts sent")


if __name__ == '__main__':
    contacts = create_contacts(randint(1, 15))
    sending_email(contacts)
