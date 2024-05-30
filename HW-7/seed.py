import random

from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

from conf.db import session
from conf.models import Grade, Group, Teacher, Student, Subject

fake = Faker('uk-UA')


GROUPS = [f"Група {chr(65+g)}" for g in range(3)]
TEACHERS = [fake.name() for t in range(5)]
STUDENTS = [fake.name() for st in range(50)]
SUBJECTS = ["Українська мова", "Математика", "Історія України", "Фізика", "Хімія", "Біологія", "Географія", "Іноземна мова",]


def ins_groups():
    for gr in GROUPS:
        group = Group(name=gr)
        session.add(group)


def ins_teachers():
    for t in TEACHERS:
        teacher = Teacher(fullname=t)
        session.add(teacher)


def ins_students():
    groups = session.query(Group).all()
    for s in STUDENTS:
        student = Student(
            fullname=s,
            group_id=random.choice(groups).id
        )
        session.add(student)


def ins_subjects():
    teachers = session.query(Teacher).all()
    for sub in SUBJECTS:
        subject = Subject(
            name=sub,
            teacher_id=random.choice(teachers).id
        )
        session.add(subject)


def ins_grades():
    students = session.query(Student).all()
    subjects = session.query(Subject).all()

    for n in range(len(students)):
        x = random.randint(1, len(subjects))
        for m in range(x):
            c = random.randint(1, 20)
            for i in range(c):
                grade = Grade(
                    grade=random.randint(1, 100),
                    date_of=fake.date_between(start_date='-4y'),
                    student_id=random.choice(students).id,
                    subject_id=random.choice(subjects).id
                )
                session.add(grade)


if __name__ == '__main__':
    try:
        ins_groups()
        ins_teachers()
        session.commit()

        ins_students()
        ins_subjects()
        session.commit()

        ins_grades()
        session.commit()

    except SQLAlchemyError as err:
        print(err)
        session.rollback()
    finally:
        session.close()
