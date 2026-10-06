-- STUDENTS
INSERT INTO Students VALUES
(101, 'Aarav Sharma', 'aarav.sharma@gmail.com', '9876543210', 'Computer Science', 8.75, 2027, 'https://resume.example/aarav');

INSERT INTO Students VALUES
(102, 'Ananya Mehta', 'ananya.mehta@gmail.com', '9876543211', 'Information Technology', 9.10, 2027, 'https://resume.example/ananya');

INSERT INTO Students VALUES
(103, 'Rohan Verma', 'rohan.verma@gmail.com', '9876543212', 'Computer Science', 7.85, 2027, 'https://resume.example/rohan');

INSERT INTO Students VALUES
(104, 'Ishita Rao', 'ishita.rao@gmail.com', '9876543213', 'Electronics', 8.45, 2026, 'https://resume.example/ishita');

INSERT INTO Students VALUES
(105, 'Kabir Singh', 'kabir.singh@gmail.com', '9876543214', 'Computer Science', 9.35, 2026, 'https://resume.example/kabir');

-- COMPANIES
INSERT INTO Companies VALUES
(201, 'TechNova Solutions', 'Information Technology', 'hr@technova.com', 'Priya Nair', 'Bangalore');

INSERT INTO Companies VALUES
(202, 'FinEdge Technologies', 'FinTech', 'careers@finedge.com', 'Rahul Kapoor', 'Mumbai');

INSERT INTO Companies VALUES
(203, 'CloudMatrix Systems', 'Cloud Computing', 'hr@cloudmatrix.com', 'Sneha Iyer', 'Hyderabad');

INSERT INTO Companies VALUES
(204, 'DataSphere Analytics', 'Data Analytics', 'hr@datasphere.com', 'Neha Sharma', 'Pune');

INSERT INTO Companies VALUES
(205, 'InnovateX Labs', 'Software', 'careers@innovatex.com', 'Arjun Malhotra', 'Chennai');

-- PLACEMENT_DRIVES
INSERT INTO Placement_Drives VALUES
(301, 201, DATE '2026-10-15', 'Main Auditorium', 'UPCOMING');

INSERT INTO Placement_Drives VALUES
(302, 202, DATE '2026-10-20', 'Placement Hall', 'UPCOMING');

INSERT INTO Placement_Drives VALUES
(303, 203, DATE '2026-09-20', 'Tech Block', 'COMPLETED');

INSERT INTO Placement_Drives VALUES
(304, 204, DATE '2026-11-05', 'Main Auditorium', 'UPCOMING');

INSERT INTO Placement_Drives VALUES
(305, 205, DATE '2026-11-15', 'Placement Hall', 'UPCOMING');

-- JOB_POSTINGS
INSERT INTO Job_Postings VALUES
(401, 301, 'Software Engineer', 'Develop and maintain software applications.', 12.50, 8.00, DATE '2026-10-10');

INSERT INTO Job_Postings VALUES
(402, 302, 'FinTech Developer', 'Build software solutions for financial applications.', 13.00, 8.50, DATE '2026-10-15');

INSERT INTO Job_Postings VALUES
(403, 303, 'Cloud Engineer', 'Design and maintain cloud infrastructure.', 14.00, 8.50, DATE '2026-09-10');

INSERT INTO Job_Postings VALUES
(404, 304, 'Data Analyst', 'Analyze business data and generate insights.', 9.00, 7.50, DATE '2026-10-30');

INSERT INTO Job_Postings VALUES
(405, 305, 'Backend Developer', 'Develop REST APIs and backend services.', 11.00, 8.00, DATE '2026-11-10');

-- APPLICATIONS
INSERT INTO Applications VALUES
(501, 101, 401, DATE '2026-10-01', 'SHORTLISTED');

INSERT INTO Applications VALUES
(502, 102, 401, DATE '2026-10-01', 'SELECTED');

INSERT INTO Applications VALUES
(503, 103, 404, DATE '2026-10-02', 'REJECTED');

INSERT INTO Applications VALUES
(504, 104, 402, DATE '2026-10-03', 'SHORTLISTED');

INSERT INTO Applications VALUES
(505, 105, 403, DATE '2026-10-01', 'SELECTED');

INSERT INTO Applications VALUES
(506, 101, 404, DATE '2026-10-03', 'APPLIED');

INSERT INTO Applications VALUES
(507, 102, 405, DATE '2026-10-04', 'APPLIED');

INSERT INTO Applications VALUES
(508, 105, 401, DATE '2026-10-02', 'SHORTLISTED');

-- INTERVIEW_ROUNDS
INSERT INTO Interview_Rounds VALUES
(601, 401, 0, 'Online Assessment');

INSERT INTO Interview_Rounds VALUES
(602, 401, 1, 'Technical Interview');

INSERT INTO Interview_Rounds VALUES
(603, 402, 0, 'Aptitude Test');

INSERT INTO Interview_Rounds VALUES
(604, 402, 1, 'Technical Interview');

INSERT INTO Interview_Rounds VALUES
(605, 403, 0, 'Coding Test');

-- INTERVIEW_RESULTS
INSERT INTO Interview_Results VALUES
(601, 501, 'PASSED');

INSERT INTO Interview_Results VALUES
(602, 501, 'PASSED');

INSERT INTO Interview_Results VALUES
(601, 502, 'PASSED');

INSERT INTO Interview_Results VALUES
(602, 502, 'PASSED');

INSERT INTO Interview_Results VALUES
(603, 504, 'PASSED');

-- OFFERS
INSERT INTO Offers VALUES
(701, 502, DATE '2026-10-25', 12.50, 'ACCEPTED');

INSERT INTO Offers VALUES
(702, 505, DATE '2026-10-28', 14.00, 'PENDING');

INSERT INTO Offers VALUES
(703, 508, DATE '2026-10-30', 12.50, 'PENDING');

INSERT INTO Offers VALUES
(704, 501, DATE '2026-10-27', 12.50, 'REJECTED');

INSERT INTO Offers VALUES
(705, 504, DATE '2026-10-29', 13.00, 'PENDING');

-- USERS
INSERT INTO Users VALUES
(801, 'aarav_student', 'HASH_AARAV', 'STUDENT', 101, NULL);

INSERT INTO Users VALUES
(802, 'ananya_student', 'HASH_ANANYA', 'STUDENT', 102, NULL);

INSERT INTO Users VALUES
(803, 'technova_hr', 'HASH_TECHNOVA', 'RECRUITER', NULL, 201);

INSERT INTO Users VALUES
(804, 'finedge_hr', 'HASH_FINEDGE', 'RECRUITER', NULL, 202);

INSERT INTO Users VALUES
(805, 'admin', 'HASH_ADMIN', 'ADMIN', NULL, NULL);

COMMIT;