SELECT t.id , t.fullname AS teacher_name, s."name" AS subject
FROM teachers t
	JOIN subjects s ON s.teacher_id = t.id
WHERE t.id = %s ;




