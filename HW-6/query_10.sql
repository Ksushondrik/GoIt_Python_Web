SELECT DISTINCT s."name" 
FROM subjects s 
	JOIN grades g ON g.subject_id = s.id 
	JOIN students st ON g.student_id = st.id 
	JOIN teachers t ON s.teacher_id = t.id 
WHERE st.id = %s AND t.id = %s;