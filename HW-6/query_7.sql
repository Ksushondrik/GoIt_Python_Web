SELECT gr."name" AS group_name , s.id , s.fullname AS student_name, g.grade 
FROM students s 
	JOIN grades g ON g.student_id = s.id 
	JOIN "groups" gr ON s.group_id = gr.id
	JOIN subjects sub ON g.subject_id = sub.id 
WHERE sub.id =  %s
ORDER BY group_name ASC, s.id ASC;
