SELECT DISTINCT s.fullname AS student_name, sub."name" AS subject_name 
FROM grades g
	JOIN students s ON g.student_id = s.id 
	JOIN subjects sub ON g.subject_id = sub.id 
WHERE s.id = %s;
