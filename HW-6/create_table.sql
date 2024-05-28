--Таблиця груп
DROP TABLE IF EXISTS groups CASCADE;
CREATE TABLE groups(
	id SERIAL PRIMARY KEY,
	name VARCHAR(50) NOT NULL
);

--Таблиця студентів
DROP TABLE IF EXISTS students CASCADE;
CREATE TABLE students(
	id SERIAL PRIMARY KEY,
	fullname VARCHAR(150) NOT NULL,
	group_id INT REFERENCES groups(id) ON DELETE CASCADE
);

--Таблиця викладачів
DROP TABLE IF EXISTS teachers CASCADE;
CREATE TABLE teachers(
	id SERIAL PRIMARY KEY,
	fullname VARCHAR(150) NOT NULL
);

--Таблиця предметів
DROP TABLE IF EXISTS subjects CASCADE;
CREATE TABLE subjects(
	id SERIAL PRIMARY KEY,
	name VARCHAR(175) NOT NULL,
	teacher_id INT REFERENCES teachers(id) ON DELETE CASCADE
);

--Таблиця оцінок
DROP TABLE IF EXISTS grades;
CREATE TABLE grades(
	id SERIAL PRIMARY KEY,
	student_id INT REFERENCES students(id) ON DELETE CASCADE,
	subject_id INT REFERENCES subjects(id) ON DELETE CASCADE,
	grade INT CHECK (grade >= 0 AND grade <= 100),
	grade_date DATE NOT NULL,
	CHECK (grade_date <= CURRENT_DATE)
);