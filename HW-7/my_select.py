from sqlalchemy import desc, func, asc

from conf.db import session
from conf.models import Grade, Group, Subject, Student, Teacher


def select_1():
    r = (
        session
        .query(
            Student.fullname,
            func.round(func.avg(Grade.grade), 2).label('avg_grade')
        )
        .select_from(Grade)
        .join(Student)
        .group_by(Student.id)
        .order_by(desc('avg_grade'))
        .limit(5)
        .all()
    )
    for i in r:
        print(i)


def select_2(subject_id: int):
    r = (
        session
        .query(
            Student.id,
            Student.fullname.label('student'),
            Subject.name.label('subject'),
            func.round(func.avg(Grade.grade), 2).label('average_grade')
        )
        .select_from(Student)
        .join(Grade)
        .join(Subject)
        .filter(Subject.id == subject_id)
        .group_by(Student.id, Student.fullname, Subject.name)
        .order_by(desc('average_grade'))
        .limit(1)
        .all()
    )
    print(r)


def select_3(subject_id):
    r = (
        session
        .query(
            Student.group_id,
            Group.name.label('group_name'),
            Subject.name,
            func.round(func.avg(Grade.grade), 2).label('average_grade')
        )
        .select_from(Student)
        .join(Grade)
        .join(Subject)
        .join(Group)
        .filter(Subject.id == subject_id)
        .group_by(Student.group_id, 'group_name', Subject.name)
        .order_by(desc('average_grade'))
        .all()
    )
    for i in r:
        print(i)


def select_4():
    r = (
        session
        .query(
            func.round(func.avg(Grade.grade), 2).label('average_grade')
        )
        .select_from(Grade)
        .all()
    )
    print(r)


def select_5(teacher_id: int):
    r = (
        session
        .query(
            Teacher.id,
            Teacher.fullname.label('teacher_name'),
            Subject.name.label('subject')
        )
        .select_from(Teacher)
        .join(Subject)
        .filter(Teacher.id == teacher_id)
        .all()
    )
    for i in r:
        print(i)


def select_6(group_id: int):
    r = (
        session
        .query(
            Student.fullname.label('student_name')
        )
        .select_from(Student)
        .filter(Student.group_id == group_id)
        .all()
    )
    for i in r:
        print(i)


def select_7(subject_id: int):
    r = (
        session
        .query(
            Group.name.label('group_name'),
            Student.id,
            Student.fullname.label('student_name'),
            Grade.grade
        )
        .select_from(Student)
        .join(Grade)
        .join(Group)
        .join(Subject)
        .filter(Subject.id == subject_id)
        .order_by(asc('group_name'), asc(Student.id))
        .all()
    )
    for i in r:
        print(i)


def select_8(teacher_id: int):
    r = (
        session
        .query(
            Subject.name.label('subject_name'),
            func.round(func.avg(Grade.grade), 2)
        )
        .select_from(Grade)
        .join(Subject)
        .join(Teacher)
        .filter(Teacher.id == teacher_id)
        .group_by(Subject.name)
        .order_by(asc('subject_name'))
        .all()
    )
    for i in r:
        print(i)


def select_9(student_id: int):
    r = (
        session
        .query(
            Student.fullname.label('student_name'),
            Subject.name.label('subject_name'),
        )
        .select_from(Grade)
        .join(Student)
        .join(Subject)
        .filter(Student.id == student_id)
        .distinct()
        .all()
    )
    for i in r:
        print(i)


def select_10(st_id: int, t_id: int):
    r = (
        session
        .query(
            Subject.name
        )
        .select_from(Subject)
        .join(Grade)
        .join(Student)
        .join(Teacher)
        .filter(Student.id == st_id, Teacher.id == t_id)
        .distinct()
        .all()
    )
    for i in r:
        print(i)


if __name__ == "__main__":
    select_1()
    select_2(2)
    select_3(3)
    select_4()
    select_5(4)
    select_6(2)
    select_7(5)
    select_8(3)
    select_9(22)
    select_10(12, 4)

