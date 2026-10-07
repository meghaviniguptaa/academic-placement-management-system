SET SQLBLANKLINES ON

/* =========================================================
   ACADEMIC PLACEMENT MANAGEMENT SYSTEM
   STORED FUNCTION
   ========================================================= */


/* =========================================================
   GET_PLACEMENT_RATE
   ---------------------------------------------------------
   Calculates placement rate as:

   Unique students with offers
   --------------------------- × 100
   Unique students who applied

   Supported scopes:
   1. OVERALL
   2. COMPANY
   3. DEPARTMENT

   For COMPANY:
       p_scope_id = Company_ID

   For DEPARTMENT:
       p_scope_id = Department name

   For OVERALL:
       p_scope_id = NULL
   ========================================================= */

CREATE OR REPLACE FUNCTION Get_Placement_Rate (
    p_scope    IN VARCHAR2,
    p_scope_id IN VARCHAR2 DEFAULT NULL
)
RETURN NUMBER
AS
    v_students_applied NUMBER := 0;
    v_students_offered NUMBER := 0;
    v_rate             NUMBER := 0;
BEGIN

    /* =====================================================
       OVERALL PLACEMENT RATE
       ===================================================== */

    IF UPPER(p_scope) = 'OVERALL' THEN

        SELECT COUNT(DISTINCT Student_ID)
        INTO v_students_applied
        FROM Applications;

        SELECT COUNT(DISTINCT a.Student_ID)
        INTO v_students_offered
        FROM Applications a
        JOIN Offers o
            ON a.Application_ID = o.Application_ID;


    /* =====================================================
       COMPANY-WISE PLACEMENT RATE
       ===================================================== */

    ELSIF UPPER(p_scope) = 'COMPANY' THEN

        SELECT COUNT(DISTINCT a.Student_ID)
        INTO v_students_applied
        FROM Applications a
        JOIN Job_Postings j
            ON a.Job_ID = j.Job_ID
        JOIN Placement_Drives pd
            ON j.Drive_ID = pd.Drive_ID
        WHERE pd.Company_ID = TO_NUMBER(p_scope_id);

        SELECT COUNT(DISTINCT a.Student_ID)
        INTO v_students_offered
        FROM Applications a
        JOIN Job_Postings j
            ON a.Job_ID = j.Job_ID
        JOIN Placement_Drives pd
            ON j.Drive_ID = pd.Drive_ID
        JOIN Offers o
            ON a.Application_ID = o.Application_ID
        WHERE pd.Company_ID = TO_NUMBER(p_scope_id);


    /* =====================================================
       DEPARTMENT-WISE PLACEMENT RATE
       ===================================================== */

    ELSIF UPPER(p_scope) = 'DEPARTMENT' THEN

        SELECT COUNT(DISTINCT a.Student_ID)
        INTO v_students_applied
        FROM Applications a
        JOIN Students s
            ON a.Student_ID = s.Student_ID
        WHERE s.Department = p_scope_id;

        SELECT COUNT(DISTINCT a.Student_ID)
        INTO v_students_offered
        FROM Applications a
        JOIN Students s
            ON a.Student_ID = s.Student_ID
        JOIN Offers o
            ON a.Application_ID = o.Application_ID
        WHERE s.Department = p_scope_id;


    ELSE

        RAISE_APPLICATION_ERROR(
            -20005,
            'Invalid scope. Use OVERALL, COMPANY or DEPARTMENT.'
        );

    END IF;


    /* =====================================================
       AVOID DIVISION BY ZERO
       ===================================================== */

    IF v_students_applied = 0 THEN
        RETURN 0;
    END IF;


    /* =====================================================
       CALCULATE PLACEMENT RATE
       ===================================================== */

    v_rate :=
        ROUND(
            (v_students_offered / v_students_applied) * 100,
            2
        );

    RETURN v_rate;

END Get_Placement_Rate;
/