import logging
from random import randint

from hw_6_insert import fake


groups = [f"Група {chr(65+g)}" for g in range(3)]
teachers = [fake.name() for t in range(5)]
students = [fake.name() for st in range(50)]
subjects = ["Українська мова", "Математика", "Історія України", "Фізика", "Хімія", "Біологія", "Географія", "Іноземна мова",]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    '''Заповнюємо таблицю груп'''
    logging.info("Inserting table groups")
    ins_groups = []
    for g in groups:
        ins_groups.append(g)
    print(ins_groups)
    logging.info("Updated table groups")

    '''Заповнюємо таблицю викладачів'''
    logging.info("Inserting table teachers")
    ins_teachers = []
    for t in teachers:
        ins_teachers.append(t)
    print(ins_teachers)
    logging.info("Updated table teachers")

    '''Заповнюємо таблицю студентів'''
    logging.info("Inserting table students")
    ins_students = {}
    for st in students:
        group_id = randint(1, len(groups))
        if group_id not in ins_students:
            ins_students[group_id] = []
        ins_students[group_id].append(st)
        # c.execute("INSERT INTO students(fullname, group_id) VALUES (%s, %s)", (st, group_id))
    for k, v in ins_students.items():
        print(k, v)
    logging.info("Updated table students")

    '''Заповнюємо таблицю предметів'''
    logging.info("Inserting table subjects")
    ins_subjects = {}
    for sub in subjects:
        teacher_id = randint(1, len(teachers))
        if teacher_id not in ins_subjects:
            ins_subjects[teacher_id] = []
        ins_subjects[teacher_id].append(sub)
        # c.execute("INSERT INTO subjects(name, teacher_id) VALUES (%s, %s)", (sub, teacher_id))
    for c, w in ins_subjects.items():
        print(c, w)
    logging.info("Updated table subjects")

    '''Заповнюємо таблицю оцінок'''
    logging.info("Inserting table grades")
    is_grades = {}
    for st in range(len(students)):
        is_sub = {}
        for sub in range(len(subjects)):
            grades = []
            for i in range(20):
                # c.execute("INSERT INTO grades(student_id, subject_id, grade, grade_date) VALUES (%s, %s, %s, %s)", (
                # st + 1, sub + 1, randint(1, 100),
                # fake.date_between(start_date=date(2020, 9, 1), end_date=date.today())))
                grades.append(randint(1, 100))
            is_sub[i] = grades
        is_grades[st] = is_sub
    for k, v in is_grades.items():
        print(k, v)
    logging.info("Updated table grades")
