
SET SQLBLANKLINES ON

-- 1. Find drives belonging to a company
CREATE INDEX idx_drives_company
ON Placement_Drives(Company_ID);

-- 2. Find jobs belonging to a placement drive
CREATE INDEX idx_jobs_drive
ON Job_Postings(Drive_ID);

-- 3. Find applications submitted by a student
CREATE INDEX idx_applications_student
ON Applications(Student_ID);

-- 4. Find applications received for a job
CREATE INDEX idx_applications_job
ON Applications(Job_ID);

-- 5. Find interview results for an application
CREATE INDEX idx_results_application
ON Interview_Results(Application_ID);
