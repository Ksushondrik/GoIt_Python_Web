SELECT s."name" AS subject_name , ROUND(AVG(g.grade),2)
FROM grades g 
	JOIN subjects s ON g.subject_id = s.id 
	JOIN teachers t ON s.teacher_id = t.id
WHERE t.id = %s
GROUP BY s."name" 
ORDER BY subject_name ASC ;
