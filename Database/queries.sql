SET SQLBLANKLINES ON

-- 1. Selection
SELECT * FROM Students WHERE CGPA > 8.5;

-- 2. Projection
SELECT Name, Department, CGPA FROM Students;

-- 3. DISTINCT
SELECT DISTINCT Department FROM Students;

-- 4. ORDER BY
SELECT Student_ID, Name, CGPA
FROM Students
ORDER BY CGPA DESC;

-- 5. Aggregates
SELECT COUNT(*) AS Total_Students FROM Students;

SELECT AVG(CGPA) AS Average_CGPA FROM Students;

SELECT MAX(CGPA) AS Highest_CGPA FROM Students;

SELECT MIN(CGPA) AS Lowest_CGPA FROM Students;

-- 6. GROUP BY
SELECT Department, COUNT(*) AS Student_Count
FROM Students
GROUP BY Department;

SELECT Job_ID, COUNT(*) AS Applicant_Count
FROM Applications
GROUP BY Job_ID;

SELECT Status, COUNT(*) AS Application_Count
FROM Applications
GROUP BY Status;

-- 7. HAVING
SELECT Job_ID, COUNT(*) AS Applicant_Count
FROM Applications
GROUP BY Job_ID
HAVING COUNT(*) > 1;

-- 8. INNER JOIN - Students and Jobs
SELECT s.Name, j.Job_Title, a.Application_Date, a.Status
FROM Students s
INNER JOIN Applications a ON s.Student_ID = a.Student_ID
INNER JOIN Job_Postings j ON a.Job_ID = j.Job_ID;

-- 9. INNER JOIN - Student, Job and Company
SELECT s.Name AS Student_Name,
       c.Company_Name,
       j.Job_Title,
       a.Status
FROM Students s
JOIN Applications a ON s.Student_ID = a.Student_ID
JOIN Job_Postings j ON a.Job_ID = j.Job_ID
JOIN Placement_Drives d ON j.Drive_ID = d.Drive_ID
JOIN Companies c ON d.Company_ID = c.Company_ID;

-- 10. LEFT JOIN
SELECT s.Student_ID, s.Name, a.Application_ID, a.Status
FROM Students s
LEFT JOIN Applications a ON s.Student_ID = a.Student_ID;

-- 11. RIGHT JOIN
SELECT j.Job_ID, j.Job_Title, a.Application_ID, a.Status
FROM Applications a
RIGHT JOIN Job_Postings j ON a.Job_ID = j.Job_ID;

-- 12. SELF JOIN
SELECT s1.Name AS Student_1,
       s2.Name AS Student_2,
       s1.CGPA AS Student_1_CGPA,
       s2.CGPA AS Student_2_CGPA
FROM Students s1
JOIN Students s2 ON s1.CGPA > s2.CGPA;

-- 13. Nested subquery - average CGPA
SELECT Name, CGPA
FROM Students
WHERE CGPA > (SELECT AVG(CGPA) FROM Students);

-- 14. Nested subquery - applications
SELECT Name
FROM Students
WHERE Student_ID IN
      (SELECT Student_ID FROM Applications);

-- 15. Correlated subquery
SELECT s1.Name, s1.Department, s1.CGPA
FROM Students s1
WHERE s1.CGPA > (
    SELECT AVG(s2.CGPA)
    FROM Students s2
    WHERE s2.Department = s1.Department
);

-- 16. UNION
SELECT Name
FROM Students
WHERE Department = 'Computer Science'
UNION
SELECT Name
FROM Students
WHERE Department = 'Information Technology';

-- 17. INTERSECT
SELECT Student_ID
FROM Students
WHERE CGPA > 8
INTERSECT
SELECT Student_ID
FROM Students
WHERE Graduation_Year = 2027;

-- 18. MINUS
SELECT Student_ID
FROM Students
MINUS
SELECT Student_ID
FROM Applications;

-- 19. Date extraction
SELECT Application_ID,
       Application_Date,
       EXTRACT(YEAR FROM Application_Date) AS Application_Year
FROM Applications;

-- 20. Date month/year
SELECT Job_ID,
       Job_Title,
       Application_Deadline
FROM Job_Postings
WHERE EXTRACT(MONTH FROM Application_Deadline) = 10
  AND EXTRACT(YEAR FROM Application_Deadline) = 2026;

-- 21. String uppercase
SELECT Name,
       UPPER(Name) AS Uppercase_Name
FROM Students;

-- 22. String length
SELECT Name,
       LENGTH(Name) AS Name_Length
FROM Students;

-- 23. Multi-table placement information
SELECT s.Name AS Student_Name,
       c.Company_Name,
       j.Job_Title,
       a.Status,
       r.Round_Number,
       r.Round_Type,
       ir.Result
FROM Students s
JOIN Applications a ON s.Student_ID = a.Student_ID
JOIN Job_Postings j ON a.Job_ID = j.Job_ID
JOIN Placement_Drives d ON j.Drive_ID = d.Drive_ID
JOIN Companies c ON d.Company_ID = c.Company_ID
LEFT JOIN Interview_Results ir ON a.Application_ID = ir.Application_ID
LEFT JOIN Interview_Rounds r ON ir.Round_ID = r.Round_ID;

-- 24. Placement summary
SELECT c.Company_Name,
       COUNT(a.Application_ID) AS Total_Applicants
FROM Companies c
JOIN Placement_Drives d ON c.Company_ID = d.Company_ID
JOIN Job_Postings j ON d.Drive_ID = j.Drive_ID
LEFT JOIN Applications a ON j.Job_ID = a.Job_ID
GROUP BY c.Company_Name
ORDER BY Total_Applicants DESC;