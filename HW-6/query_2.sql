SELECT s.id, s.fullname AS student, s2."name" AS subject, 
ROUND(AVG(g.grade), 2) AS average_grade
FROM students s 
	JOIN grades g ON s.id = g.student_id 
	JOIN subjects s2 ON s2.id = g.subject_id
WHERE s2.id = %s
GROUP BY s.id, s.fullname , s2."name"
ORDER BY average_grade DESC
LIMIT 1;
