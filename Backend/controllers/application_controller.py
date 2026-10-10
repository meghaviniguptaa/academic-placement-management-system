from datetime import date
from config.db import get_connection


# --------------------------------------------------
# GET ALL APPLICATIONS (existing CRUD)
# --------------------------------------------------
def get_all_applications():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT Application_ID, Student_ID, Job_ID,
                   Application_Date, Status
            FROM Applications
        """)

        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


# --------------------------------------------------
# CREATE APPLICATION (existing CRUD)
# --------------------------------------------------
def create_application(application):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO Applications
                (Application_ID, Student_ID, Job_ID,
                 Application_Date, Status)
            VALUES
                (:1, :2, :3, TO_DATE(:4, 'YYYY-MM-DD'), :5)
        """, (
            application["Application_ID"],
            application["Student_ID"],
            application["Job_ID"],
            application["Application_Date"],
            application["Status"]
        ))

        connection.commit()

    except Exception:
        if connection is not None:
            connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


# --------------------------------------------------
# UPDATE APPLICATION (existing CRUD)
# --------------------------------------------------
def update_application(application_id, application):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE Applications
            SET Student_ID = :1,
                Job_ID = :2,
                Application_Date = TO_DATE(:3, 'YYYY-MM-DD'),
                Status = :4
            WHERE Application_ID = :5
        """, (
            application["Student_ID"],
            application["Job_ID"],
            application["Application_Date"],
            application["Status"],
            application_id
        ))

        rows_updated = cursor.rowcount
        connection.commit()

        return rows_updated

    except Exception:
        if connection is not None:
            connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


# --------------------------------------------------
# DELETE APPLICATION (existing CRUD)
# --------------------------------------------------
def delete_application(application_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM Applications
            WHERE Application_ID = :1
        """, (application_id,))

        rows_deleted = cursor.rowcount
        connection.commit()

        return rows_deleted

    except Exception:
        if connection is not None:
            connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


# --------------------------------------------------
# GET APPLICATIONS FOR THE LOGGED-IN STUDENT
# --------------------------------------------------
def get_my_applications(student_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                a.Application_ID,
                a.Job_ID,
                j.Job_Title,
                c.Company_Name,
                a.Application_Date,
                a.Status,
                j.Package_LPA,
                j.Application_Deadline
            FROM Applications a
            JOIN Job_Postings j
                ON a.Job_ID = j.Job_ID
            JOIN Placement_Drives d
                ON j.Drive_ID = d.Drive_ID
            JOIN Companies c
                ON d.Company_ID = c.Company_ID
            WHERE a.Student_ID = :1
            ORDER BY a.Application_Date DESC,
                     a.Application_ID DESC
        """, (student_id,))

        columns = [col[0] for col in cursor.description]

        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


# --------------------------------------------------
# APPLY FOR A JOB
# --------------------------------------------------
def apply_for_job(student_id, job_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Check student eligibility and job availability.
        cursor.execute("""
            SELECT
                s.CGPA,
                j.Min_CGPA_Requirement,
                j.Application_Deadline,
                d.Drive_Status
            FROM Students s
            CROSS JOIN Job_Postings j
            JOIN Placement_Drives d
                ON j.Drive_ID = d.Drive_ID
            WHERE s.Student_ID = :student_id
              AND j.Job_ID = :job_id
        """, {
            "student_id": student_id,
            "job_id": job_id
        })

        job = cursor.fetchone()

        if not job:
            return {
                "message": "Student or job not found."
            }, 404

        student_cgpa, min_cgpa, deadline, drive_status = job

        if student_cgpa < min_cgpa:
            return {
                "message": "You do not meet the minimum CGPA requirement."
            }, 400

        if deadline.date() < date.today():
            return {
                "message": "The application deadline has passed."
            }, 400

        if drive_status not in ("UPCOMING", "ONGOING"):
            return {
                "message": "Applications are not open for this drive."
            }, 400

        # Check whether this student has already applied.
        cursor.execute("""
            SELECT 1
            FROM Applications
            WHERE Student_ID = :1
              AND Job_ID = :2
        """, (student_id, job_id))

        if cursor.fetchone():
            return {
                "message": "You have already applied for this job."
            }, 409

        # Insert using the Oracle sequence.
        cursor.execute("""
            INSERT INTO Applications
                (Application_ID, Student_ID, Job_ID,
                 Application_Date, Status)
            VALUES
                (Applications_Seq.NEXTVAL, :1, :2,
                 SYSDATE, 'APPLIED')
        """, (student_id, job_id))

        cursor.execute("""
            SELECT Applications_Seq.CURRVAL
            FROM DUAL
        """)

        application_id = cursor.fetchone()[0]

        connection.commit()

        return {
            "message": "Application submitted successfully.",
            "Application_ID": application_id
        }, 201

    except Exception:
        if connection is not None:
            connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
