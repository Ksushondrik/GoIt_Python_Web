import time

import pika
from mongoengine.errors import DoesNotExist
from producer import Contact

count = 0


def sending_email(contact: Contact):
    print(f"Sending email to {contact.email}...")
    time.sleep(2)
    print(f"Sent email to {contact.email}")


def callback(ch, method, properties, body):
    global count
    cont_id = body.decode()
    try:
        contact = Contact.objects.get(id=cont_id)
        sending_email(contact)
        contact.sent = True
        contact.save()
        print(f"Contact {cont_id} updated")
        count += 1
        print(f'[x] Total emails sent: {count}')
    except DoesNotExist:
        print(f"Contact with id {cont_id} not found")
        return
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    credentials = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
    channel = connection.channel()

    channel.exchange_declare(exchange='HW_8', exchange_type='fanout', durable=True)
    channel.queue_declare(queue='mail_queue', durable=True)
    channel.queue_bind(exchange="HW_8", queue="mail_queue")

    channel.basic_consume(queue='mail_queue', on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
