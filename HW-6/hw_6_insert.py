import logging
from random import randint
from datetime import date

from faker import Faker
from psycopg2 import DatabaseError

from create import create_connection


logging.basicConfig(level=logging.INFO)

fake = Faker('uk-Ua')


groups = [f"Група {chr(65+g)}" for g in range(3)]
teachers = [fake.name() for t in range(5)]
students = [fake.name() for st in range(50)]
subjects = ["Українська мова", "Математика", "Історія України", "Фізика", "Хімія", "Біологія", "Географія", "Іноземна мова",]


def insert_data(conn):
    c = conn.cursor()
    try:
        '''Заповнюємо таблицю груп'''
        logging.info("Inserting table groups")
        for g in groups:
            c.execute("INSERT INTO groups(name) VALUES (%s)", (g,))
        logging.info("Updated table groups")

        '''Заповнюємо таблицю викладачів'''
        logging.info("Inserting table teachers")
        for t in teachers:
            c.execute("INSERT INTO teachers(fullname) VALUES (%s)", (t,))
        logging.info("Updated table teachers")

        '''Заповнюємо таблицю студентів'''
        logging.info("Inserting table students")
        for st in students:
            group_id = randint(1, len(groups))
            c.execute("INSERT INTO students(fullname, group_id) VALUES (%s, %s)", (st, group_id))
        logging.info("Updated table students")

        '''Заповнюємо таблицю предметів'''
        logging.info("Inserting table subjects")
        for sub in subjects:
            teacher_id = randint(1, len(teachers))
            c.execute("INSERT INTO subjects(name, teacher_id) VALUES (%s, %s)", (sub, teacher_id))
        logging.info("Updated table subjects")

        '''Заповнюємо таблицю оцінок'''
        logging.info("Inserting table grades")
        for st in range(len(students)):
            for sub in range(len(subjects)):
                for _ in range(20):
                    c.execute("INSERT INTO grades(student_id, subject_id, grade, grade_date) VALUES (%s, %s, %s, %s)", (st + 1, sub + 1, randint(1, 100), fake.date_between(start_date=date(2020, 9, 1), end_date=date.today())))
        logging.info("Updated table grades")

        conn.commit()
        logging.info("The table has been successfully filled.")
    except DatabaseError as err:
        logging.error(f"Database error: {err}")
        conn.rollback()
    except Exception as err:
        logging.error(f"Error: {err}")
        conn.rollback()
    finally:
        c.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        with create_connection() as conn:
            if conn is not None:
                logging.info("Inserting data...")
                insert_data(conn)
                logging.info("The table has been successfully filled.")
            else:
                logging.error("Error! Cannot create the database connection.")
    except RuntimeError as err:
        logging.error(f"Runtime error: {err}")
