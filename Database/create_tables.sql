-- 1. STUDENTS
CREATE TABLE Students (
    Student_ID NUMBER PRIMARY KEY,
    Name VARCHAR2(100) NOT NULL,
    Email VARCHAR2(100) NOT NULL UNIQUE,
    Phone VARCHAR2(15),
    Department VARCHAR2(100),
    CGPA NUMBER(4,2),
    Graduation_Year NUMBER(4),
    Resume_URL VARCHAR2(255),

    CONSTRAINT chk_student_cgpa
        CHECK (CGPA BETWEEN 0 AND 10),

    CONSTRAINT chk_graduation_year
        CHECK (Graduation_Year >= 2026)
);


-- 2. COMPANIES
CREATE TABLE Companies (
    Company_ID NUMBER PRIMARY KEY,
    Company_Name VARCHAR2(150) NOT NULL,
    Industry VARCHAR2(100),
    Contact_Email VARCHAR2(100) NOT NULL UNIQUE,
    HR_Name VARCHAR2(100) NOT NULL,
    Location VARCHAR2(150)
);


-- 3. PLACEMENT DRIVES
CREATE TABLE Placement_Drives (
    Drive_ID NUMBER PRIMARY KEY,
    Company_ID NUMBER NOT NULL,
    Drive_Date DATE NOT NULL,
    Venue VARCHAR2(150),

    Drive_Status VARCHAR2(20) DEFAULT 'UPCOMING',

    CONSTRAINT chk_drive_status
        CHECK (Drive_Status IN
        ('UPCOMING', 'ONGOING', 'COMPLETED', 'CANCELLED')),

    CONSTRAINT fk_drive_company
        FOREIGN KEY (Company_ID)
        REFERENCES Companies(Company_ID)
);


-- 4. JOB POSTINGS
CREATE TABLE Job_Postings (
    Job_ID NUMBER PRIMARY KEY,
    Drive_ID NUMBER NOT NULL,
    Job_Title VARCHAR2(150) NOT NULL,
    Role_Description VARCHAR2(1000),
    Package_LPA NUMBER(6,2),
    Min_CGPA_Requirement NUMBER(4,2),
    Application_Deadline DATE NOT NULL,

    CONSTRAINT chk_job_package
        CHECK (Package_LPA > 0),

    CONSTRAINT chk_job_min_cgpa
        CHECK (Min_CGPA_Requirement BETWEEN 0 AND 10),

    CONSTRAINT fk_job_drive
        FOREIGN KEY (Drive_ID)
        REFERENCES Placement_Drives(Drive_ID)
);


-- 5. APPLICATIONS
CREATE TABLE Applications (
    Application_ID NUMBER PRIMARY KEY,
    Student_ID NUMBER NOT NULL,
    Job_ID NUMBER NOT NULL,

    Application_Date DATE DEFAULT SYSDATE NOT NULL,

    Status VARCHAR2(20) DEFAULT 'APPLIED',

    CONSTRAINT chk_application_status
        CHECK (Status IN
        ('APPLIED', 'SHORTLISTED', 'REJECTED',
         'SELECTED', 'WITHDRAWN')),

    CONSTRAINT fk_application_student
        FOREIGN KEY (Student_ID)
        REFERENCES Students(Student_ID),

    CONSTRAINT fk_application_job
        FOREIGN KEY (Job_ID)
        REFERENCES Job_Postings(Job_ID),

    CONSTRAINT uq_student_job
        UNIQUE (Student_ID, Job_ID)
);


-- 6. INTERVIEW ROUNDS
CREATE TABLE Interview_Rounds (
    Round_ID NUMBER PRIMARY KEY,
    Job_ID NUMBER NOT NULL,

    Round_Number NUMBER NOT NULL,

    Round_Type VARCHAR2(50) NOT NULL,

    CONSTRAINT chk_round_number
        CHECK (Round_Number >= 0),

    CONSTRAINT fk_round_job
        FOREIGN KEY (Job_ID)
        REFERENCES Job_Postings(Job_ID),

    CONSTRAINT uq_job_round
        UNIQUE (Job_ID, Round_Number)
);


-- 7. INTERVIEW RESULTS
CREATE TABLE Interview_Results (
    Round_ID NUMBER,
    Application_ID NUMBER,

    Result VARCHAR2(20) DEFAULT 'PENDING',

    CONSTRAINT pk_interview_result
        PRIMARY KEY (Round_ID, Application_ID),

    CONSTRAINT chk_interview_result
        CHECK (Result IN ('PENDING', 'PASSED', 'FAILED')),

    CONSTRAINT fk_result_round
        FOREIGN KEY (Round_ID)
        REFERENCES Interview_Rounds(Round_ID),

    CONSTRAINT fk_result_application
        FOREIGN KEY (Application_ID)
        REFERENCES Applications(Application_ID)
);


-- 8. OFFERS
CREATE TABLE Offers (
    Offer_ID NUMBER PRIMARY KEY,
    Application_ID NUMBER NOT NULL UNIQUE,

    Offer_Date DATE DEFAULT SYSDATE NOT NULL,

    Offered_Package_LPA NUMBER(6,2),

    Offer_Status VARCHAR2(20) DEFAULT 'PENDING',

    CONSTRAINT chk_offer_package
        CHECK (Offered_Package_LPA > 0),

    CONSTRAINT chk_offer_status
        CHECK (Offer_Status IN
        ('PENDING', 'ACCEPTED', 'REJECTED')),

    CONSTRAINT fk_offer_application
        FOREIGN KEY (Application_ID)
        REFERENCES Applications(Application_ID)
);


-- 9. USERS
CREATE TABLE Users (
    User_ID NUMBER PRIMARY KEY,

    Username VARCHAR2(50) NOT NULL UNIQUE,

    Password_Hash VARCHAR2(255) NOT NULL,

    Role VARCHAR2(20) NOT NULL,

    Student_ID NUMBER,
    Company_ID NUMBER,

    CONSTRAINT chk_user_role
        CHECK (Role IN ('STUDENT', 'RECRUITER', 'ADMIN')),

    CONSTRAINT fk_user_student
        FOREIGN KEY (Student_ID)
        REFERENCES Students(Student_ID),

    CONSTRAINT fk_user_company
        FOREIGN KEY (Company_ID)
        REFERENCES Companies(Company_ID)
);
