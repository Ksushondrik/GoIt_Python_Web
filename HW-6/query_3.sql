SELECT s.group_id, gr."name" AS group_name, sub."name" ,
	ROUND(AVG(g.grade),2) AS average_grade
FROM students s 
	JOIN grades g ON s.id = g.student_id 
	JOIN subjects sub ON g.subject_id = sub.id
	JOIN "groups" gr ON s.group_id = gr.id 
WHERE sub.id  = %s
GROUP BY s.group_id, group_name, sub."name" 
ORDER BY average_grade DESC;
