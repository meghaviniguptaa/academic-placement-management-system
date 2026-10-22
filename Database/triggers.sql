SET SQLBLANKLINES ON

/* =========================================================
   ACADEMIC PLACEMENT MANAGEMENT SYSTEM
   DATABASE TRIGGERS
   ========================================================= */


/* =========================================================
   1. VALIDATE INTERVIEW RESULT
   ---------------------------------------------------------
   Ensures that an interview result can only be recorded
   when the interview round and application belong to
   the same job.
   ========================================================= */

CREATE OR REPLACE TRIGGER TRG_VALIDATE_INTERVIEW_RESULT
BEFORE INSERT OR UPDATE ON Interview_Results
FOR EACH ROW
DECLARE
    v_round_job_id       Interview_Rounds.Job_ID%TYPE;
    v_application_job_id Applications.Job_ID%TYPE;
BEGIN

    /* Find the job associated with the interview round */
    SELECT Job_ID
    INTO v_round_job_id
    FROM Interview_Rounds
    WHERE Round_ID = :NEW.Round_ID;


    /* Find the job associated with the application */
    SELECT Job_ID
    INTO v_application_job_id
    FROM Applications
    WHERE Application_ID = :NEW.Application_ID;


    /* Both must belong to the same job */
    IF v_round_job_id <> v_application_job_id THEN

        RAISE_APPLICATION_ERROR(
            -20010,
            'Interview round and application belong to different jobs.'
        );

    END IF;

END;
/


/* =========================================================
   2. VALIDATE USER ROLE
   ---------------------------------------------------------
   Ensures that Student_ID and Company_ID match the
   assigned user role.
   ========================================================= */

CREATE OR REPLACE TRIGGER TRG_VALIDATE_USER_ROLE
BEFORE INSERT OR UPDATE ON Users
FOR EACH ROW
BEGIN

    /* STUDENT must have Student_ID only */
    IF :NEW.Role = 'STUDENT' THEN

        IF :NEW.Student_ID IS NULL
           OR :NEW.Company_ID IS NOT NULL
        THEN

            RAISE_APPLICATION_ERROR(
                -20011,
                'STUDENT role requires Student_ID and no Company_ID.'
            );

        END IF;

    END IF;


    /* RECRUITER must have Company_ID only */
    IF :NEW.Role = 'RECRUITER' THEN

        IF :NEW.Company_ID IS NULL
           OR :NEW.Student_ID IS NOT NULL
        THEN

            RAISE_APPLICATION_ERROR(
                -20012,
                'RECRUITER role requires Company_ID and no Student_ID.'
            );

        END IF;

    END IF;


    /* ADMIN must not be linked to a student or company */
    IF :NEW.Role = 'ADMIN' THEN

        IF :NEW.Student_ID IS NOT NULL
           OR :NEW.Company_ID IS NOT NULL
        THEN

            RAISE_APPLICATION_ERROR(
                -20013,
                'ADMIN role cannot have Student_ID or Company_ID.'
            );

        END IF;

    END IF;

END;
/