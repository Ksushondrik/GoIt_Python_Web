import logging

from psycopg2 import DatabaseError

from connect import create_connection

queryset = [
    "1 -> Знайти 5 студентів із найбільшим середнім балом з усіх предметів.",
    "2 -> Знайти студента із найвищим середнім балом з певного предмета.",
    "3 -> Знайти середній бал у групах з певного предмета.",
    "4 -> Знайти середній бал на потоці (по всій таблиці оцінок).",
    "5 -> Знайти які курси читає певний викладач.",
    "6 -> Знайти список студентів у певній групі.",
    "7 -> Знайти оцінки студентів у окремій групі з певного предмета.",
    "8 -> Знайти середній бал, який ставить певний викладач зі своїх предметів.",
    "9 -> Знайти список курсів, які відвідує студент.",
    "10 -> Список курсів, які певному студенту читає певний викладач."
]


def read_sql_script(script_number: int):
    filename = f"query_{script_number}.sql"
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            sql_script = file.read()
        return sql_script
    except FileNotFoundError as err:
        logging.error(f"File not found error: {err}")
        return None


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    for i in queryset:
        print(i)
    n = int(input("Введіть номер обраного запиту: "))
    # params = {}
    if n == 10:
        student_id = int(input("Введіть ID студента: "))
        teacher_id = int(input("ВВедіть ID вчителя: "))
        params = (student_id, teacher_id)
        # params["student_id"] = student_id
        # params["teacher_id"] = teacher_id
    elif n in [7, 3, 2]:
        subject_id = input("Введіть ID предмету: ")
        params = (subject_id, )
        # params["subject_id"] = subject_id
    elif n in [8, 5]:
        teacher_id = input("Введіть ID викладача: ")
        params = (teacher_id, )
        # params['teacher_id'] = teacher_id
    elif n in [9, 6]:
        student_id = input("Введіть ID студента: ")
        params = (student_id, )
        # params["student_id"] = student_id

    try:
        sql_expression = read_sql_script(n)
        if sql_expression:
            with create_connection() as conn:
                if conn is not None:
                    c = conn.cursor()
                    try:
                        if n in [1, 4]:
                            c.execute(sql_expression)
                        else:
                            # numeric_values = [int(value) for value in params.values()]
                            # tup_params = tuple(numeric_values)
                            # c.execute(sql_expression, tup_params)
                            c.execute(sql_expression, params)
                        result = c.fetchall()
                        for row in result:
                            print(row)

                    except DatabaseError as err:
                        logging.error(f"Database error: {err}")
                    finally:
                        c.close()
                else:
                    logging.error("Error! Cannot create the database connection.")
        else:
            logging.error("Error! Cannot read the SQL script.")
    except RuntimeError as err:
        logging.error(f"Runtime error: {err}")
    except Exception as err:
        logging.error(f"Unexpected error: {err}")
