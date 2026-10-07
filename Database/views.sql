SET SQLBLANKLINES ON

/* =========================================================
   ACADEMIC PLACEMENT MANAGEMENT SYSTEM
   ROLE-BASED DATABASE VIEWS
   ========================================================= */


/* =========================================================
   1. STUDENT APPLICATION VIEW
   Shows applications submitted by students along with
   job, company, package and application status.
   ========================================================= */

CREATE OR REPLACE VIEW Student_Application_View AS
SELECT
    s.Student_ID,
    s.Name AS Student_Name,
    s.Department,
    s.CGPA,

    a.Application_ID,
    a.Application_Date,
    a.Status AS Application_Status,

    j.Job_ID,
    j.Job_Title,
    j.Package_LPA,
    j.Application_Deadline,

    pd.Drive_ID,
    pd.Drive_Date,
    pd.Drive_Status,

    c.Company_ID,
    c.Company_Name,
    c.Industry

FROM Students s
JOIN Applications a
    ON s.Student_ID = a.Student_ID
JOIN Job_Postings j
    ON a.Job_ID = j.Job_ID
JOIN Placement_Drives pd
    ON j.Drive_ID = pd.Drive_ID
JOIN Companies c
    ON pd.Company_ID = c.Company_ID;


/* =========================================================
   2. STUDENT INTERVIEW & OFFER VIEW
   Shows interview rounds, results and offer information
   associated with a student's applications.
   ========================================================= */

CREATE OR REPLACE VIEW Student_Interview_Offer_View AS
SELECT
    s.Student_ID,
    s.Name AS Student_Name,

    a.Application_ID,
    a.Status AS Application_Status,

    j.Job_ID,
    j.Job_Title,

    c.Company_ID,
    c.Company_Name,

    ir.Round_ID,
    ir.Round_Number,
    ir.Round_Type,

    res.Result AS Interview_Result,

    o.Offer_ID,
    o.Offer_Date,
    o.Offered_Package_LPA,
    o.Offer_Status

FROM Students s
JOIN Applications a
    ON s.Student_ID = a.Student_ID
JOIN Job_Postings j
    ON a.Job_ID = j.Job_ID
JOIN Placement_Drives pd
    ON j.Drive_ID = pd.Drive_ID
JOIN Companies c
    ON pd.Company_ID = c.Company_ID

LEFT JOIN Interview_Results res
    ON a.Application_ID = res.Application_ID

LEFT JOIN Interview_Rounds ir
    ON res.Round_ID = ir.Round_ID

LEFT JOIN Offers o
    ON a.Application_ID = o.Application_ID;


/* =========================================================
   3. STUDENT ELIGIBLE JOBS VIEW
   Shows jobs for which the student's CGPA satisfies
   the minimum requirement and the application deadline
   has not passed.
   ========================================================= */

CREATE OR REPLACE VIEW Student_Eligible_Jobs_View AS
SELECT
    s.Student_ID,
    s.Name AS Student_Name,
    s.CGPA AS Student_CGPA,

    j.Job_ID,
    j.Job_Title,
    j.Role_Description,
    j.Package_LPA,
    j.Min_CGPA_Requirement,
    j.Application_Deadline,

    pd.Drive_ID,
    pd.Drive_Date,
    pd.Drive_Status,

    c.Company_ID,
    c.Company_Name,
    c.Industry

FROM Students s
JOIN Job_Postings j
    ON s.CGPA >= j.Min_CGPA_Requirement
JOIN Placement_Drives pd
    ON j.Drive_ID = pd.Drive_ID
JOIN Companies c
    ON pd.Company_ID = c.Company_ID

WHERE j.Application_Deadline >= TRUNC(SYSDATE)
  AND pd.Drive_Status IN ('UPCOMING', 'ONGOING');


/* =========================================================
   4. RECRUITER DRIVE ANALYTICS VIEW
   Shows each company's drives, roles and the number
   of applications received for each role.
   ========================================================= */

CREATE OR REPLACE VIEW Recruiter_Drive_Analytics_View AS
SELECT
    c.Company_ID,
    c.Company_Name,

    pd.Drive_ID,
    pd.Drive_Date,
    pd.Venue,
    pd.Drive_Status,

    j.Job_ID,
    j.Job_Title,
    j.Package_LPA,

    COUNT(a.Application_ID) AS Application_Count

FROM Companies c
JOIN Placement_Drives pd
    ON c.Company_ID = pd.Company_ID
JOIN Job_Postings j
    ON pd.Drive_ID = j.Drive_ID
LEFT JOIN Applications a
    ON j.Job_ID = a.Job_ID

GROUP BY
    c.Company_ID,
    c.Company_Name,
    pd.Drive_ID,
    pd.Drive_Date,
    pd.Venue,
    pd.Drive_Status,
    j.Job_ID,
    j.Job_Title,
    j.Package_LPA;


/* =========================================================
   5. RECRUITER ROUND ANALYTICS VIEW
   Shows round-wise candidate results:
   PASSED, FAILED and PENDING.
   ========================================================= */

CREATE OR REPLACE VIEW Recruiter_Round_Analytics_View AS
SELECT
    c.Company_ID,
    c.Company_Name,

    pd.Drive_ID,

    j.Job_ID,
    j.Job_Title,

    ir.Round_ID,
    ir.Round_Number,
    ir.Round_Type,

    COUNT(res.Application_ID) AS Candidates_In_Round,

    SUM(
        CASE
            WHEN res.Result = 'PASSED' THEN 1
            ELSE 0
        END
    ) AS Passed_Count,

    SUM(
        CASE
            WHEN res.Result = 'FAILED' THEN 1
            ELSE 0
        END
    ) AS Failed_Count,

    SUM(
        CASE
            WHEN res.Result = 'PENDING' THEN 1
            ELSE 0
        END
    ) AS Pending_Count

FROM Companies c
JOIN Placement_Drives pd
    ON c.Company_ID = pd.Company_ID
JOIN Job_Postings j
    ON pd.Drive_ID = j.Drive_ID
JOIN Interview_Rounds ir
    ON j.Job_ID = ir.Job_ID
LEFT JOIN Interview_Results res
    ON ir.Round_ID = res.Round_ID

GROUP BY
    c.Company_ID,
    c.Company_Name,
    pd.Drive_ID,
    j.Job_ID,
    j.Job_Title,
    ir.Round_ID,
    ir.Round_Number,
    ir.Round_Type;


/* =========================================================
   6. ADMIN PLACEMENT OVERVIEW VIEW
   Provides department-wise placement statistics.

   Each row represents one department.
   Overall system statistics are provided separately
   by Admin_System_Summary_View.
   ========================================================= */

CREATE OR REPLACE VIEW Admin_Placement_Overview_View AS
SELECT
    s.Department,

    COUNT(DISTINCT s.Student_ID) AS Total_Students,

    COUNT(
        DISTINCT CASE
            WHEN a.Application_ID IS NOT NULL
            THEN s.Student_ID
        END
    ) AS Students_Applied,

    COUNT(
        DISTINCT CASE
            WHEN o.Offer_ID IS NOT NULL
            THEN s.Student_ID
        END
    ) AS Students_With_Offers

FROM Students s

LEFT JOIN Applications a
    ON s.Student_ID = a.Student_ID

LEFT JOIN Offers o
    ON a.Application_ID = o.Application_ID

GROUP BY
    s.Department;


/* =========================================================
   7. ADMIN COMPANY PERFORMANCE VIEW
   Shows company-wise drives, roles, applications and offers.
   ========================================================= */

CREATE OR REPLACE VIEW Admin_Company_Performance_View AS
SELECT
    c.Company_ID,
    c.Company_Name,
    c.Industry,

    COUNT(DISTINCT pd.Drive_ID) AS Total_Drives,

    COUNT(DISTINCT j.Job_ID) AS Total_Roles,

    COUNT(DISTINCT a.Application_ID) AS Total_Applications,

    COUNT(DISTINCT o.Offer_ID) AS Total_Offers

FROM Companies c

LEFT JOIN Placement_Drives pd
    ON c.Company_ID = pd.Company_ID

LEFT JOIN Job_Postings j
    ON pd.Drive_ID = j.Drive_ID

LEFT JOIN Applications a
    ON j.Job_ID = a.Job_ID

LEFT JOIN Offers o
    ON a.Application_ID = o.Application_ID

GROUP BY
    c.Company_ID,
    c.Company_Name,
    c.Industry;


/* =========================================================
   8. ADMIN SYSTEM SUMMARY VIEW
   Provides overall placement statistics for the
   administrator dashboard.

   This view returns exactly one summary row.
   ========================================================= */

CREATE OR REPLACE VIEW Admin_System_Summary_View AS
SELECT
    (SELECT COUNT(*)
     FROM Students) AS Total_Students,

    (SELECT COUNT(DISTINCT Company_ID)
     FROM Placement_Drives) AS Companies_With_Drives,

    (SELECT COUNT(*)
     FROM Placement_Drives) AS Total_Drives,

    (SELECT COUNT(*)
     FROM Job_Postings) AS Total_Roles,

    (SELECT COUNT(DISTINCT Student_ID)
     FROM Applications) AS Students_Applied,

    (SELECT COUNT(*)
     FROM Applications) AS Total_Applications,

    (SELECT COUNT(*)
     FROM Offers) AS Total_Offers,

    (SELECT COUNT(DISTINCT Application_ID)
     FROM Offers) AS Students_With_Offers

FROM DUAL;