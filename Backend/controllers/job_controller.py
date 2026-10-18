from config.db import get_connection


def get_all_jobs():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT Job_ID, Drive_ID, Job_Title, Role_Description,
               Package_LPA, Min_CGPA_Requirement, Application_Deadline
        FROM Job_Postings
    """)

    columns = [col[0] for col in cursor.description]
    jobs = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return jobs


def create_job(job):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO Job_Postings
        (Job_ID, Drive_ID, Job_Title, Role_Description,
         Package_LPA, Min_CGPA_Requirement, Application_Deadline)
        VALUES
        (:1, :2, :3, :4, :5, :6, :7)
    """, (
        job["Job_ID"],
        job["Drive_ID"],
        job["Job_Title"],
        job["Role_Description"],
        job["Package_LPA"],
        job["Min_CGPA_Requirement"],
        job["Application_Deadline"]
    ))

    connection.commit()

    cursor.close()
    connection.close()


def update_job(job_id, job):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE Job_Postings
        SET Drive_ID = :1,
            Job_Title = :2,
            Role_Description = :3,
            Package_LPA = :4,
            Min_CGPA_Requirement = :5,
            Application_Deadline = :6
        WHERE Job_ID = :7
    """, (
        job["Drive_ID"],
        job["Job_Title"],
        job["Role_Description"],
        job["Package_LPA"],
        job["Min_CGPA_Requirement"],
        job["Application_Deadline"],
        job_id
    ))

    rows_updated = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    return rows_updated


def delete_job(job_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM Job_Postings
        WHERE Job_ID = :1
    """, (job_id,))

    rows_deleted = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    return rows_deleted


# --------------------------------------------------
# GET AVAILABLE JOBS FOR STUDENTS
# --------------------------------------------------
def get_student_jobs(search=None, min_package=None, max_package=None):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
            SELECT
                j.Job_ID,
                j.Job_Title,
                j.Role_Description,
                j.Package_LPA,
                j.Min_CGPA_Requirement,
                j.Application_Deadline,
                c.Company_Name,
                d.Drive_Date,
                d.Drive_Status
            FROM Job_Postings j
            JOIN Placement_Drives d
                ON j.Drive_ID = d.Drive_ID
            JOIN Companies c
                ON d.Company_ID = c.Company_ID
            WHERE j.Application_Deadline >= TRUNC(SYSDATE)
              AND d.Drive_Status IN ('UPCOMING', 'ONGOING')
        """

        params = {}

        if search:
            query += """
                AND (
                    LOWER(j.Job_Title) LIKE :search
                    OR LOWER(c.Company_Name) LIKE :search
                )
            """
            params["search"] = f"%{search.strip().lower()}%"

        if min_package is not None:
            query += " AND j.Package_LPA >= :min_package"
            params["min_package"] = min_package

        if max_package is not None:
            query += " AND j.Package_LPA <= :max_package"
            params["max_package"] = max_package

        query += " ORDER BY j.Application_Deadline, j.Job_ID"

        cursor.execute(query, params)

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
# GET DETAILS OF ONE AVAILABLE JOB
# --------------------------------------------------
def get_student_job_details(job_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                j.Job_ID,
                j.Job_Title,
                j.Role_Description,
                j.Package_LPA,
                j.Min_CGPA_Requirement,
                j.Application_Deadline,
                c.Company_Name,
                c.Industry,
                c.Location,
                d.Drive_Date,
                d.Venue,
                d.Drive_Status
            FROM Job_Postings j
            JOIN Placement_Drives d
                ON j.Drive_ID = d.Drive_ID
            JOIN Companies c
                ON d.Company_ID = c.Company_ID
            WHERE j.Job_ID = :1
              AND j.Application_Deadline >= TRUNC(SYSDATE)
              AND d.Drive_Status IN ('UPCOMING', 'ONGOING')
        """, (job_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row))

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

# --------------------------------------------------
# RECRUITER JOB MANAGEMENT
# --------------------------------------------------

def get_company_jobs(company_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT j.Job_ID,
               j.Drive_ID,
               j.Job_Title,
               j.Role_Description,
               j.Package_LPA,
               j.Min_CGPA_Requirement,
               j.Application_Deadline
        FROM Job_Postings j
        JOIN Placement_Drives d
            ON j.Drive_ID = d.Drive_ID
        WHERE d.Company_ID = :1
        ORDER BY j.Job_ID
    """, (company_id,))

    columns = [col[0] for col in cursor.description]
    jobs = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return jobs


def create_company_job(company_id, job):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO Job_Postings
        (Job_ID, Drive_ID, Job_Title, Role_Description,
         Package_LPA, Min_CGPA_Requirement, Application_Deadline)
        SELECT :1, Drive_ID, :2, :3, :4, :5, :6
        FROM Placement_Drives
        WHERE Drive_ID = :7
          AND Company_ID = :8
    """, (
        job["Job_ID"],
        job["Job_Title"],
        job["Role_Description"],
        job["Package_LPA"],
        job["Min_CGPA_Requirement"],
        job["Application_Deadline"],
        job["Drive_ID"],
        company_id
    ))

    if cursor.rowcount == 0:
        connection.rollback()
        cursor.close()
        connection.close()
        raise ValueError("Drive does not belong to your company.")

    connection.commit()

    cursor.close()
    connection.close()


def update_company_job(company_id, job_id, job):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE Job_Postings j
        SET j.Job_Title = :1,
            j.Role_Description = :2,
            j.Package_LPA = :3,
            j.Min_CGPA_Requirement = :4,
            j.Application_Deadline = :5
        WHERE j.Job_ID = :6
          AND EXISTS (
              SELECT 1
              FROM Placement_Drives d
              WHERE d.Drive_ID = j.Drive_ID
                AND d.Company_ID = :7
          )
    """, (
        job["Job_Title"],
        job["Role_Description"],
        job["Package_LPA"],
        job["Min_CGPA_Requirement"],
        job["Application_Deadline"],
        job_id,
        company_id
    ))

    rows_updated = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    return rows_updated


def delete_company_job(company_id, job_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM Job_Postings j
        WHERE j.Job_ID = :1
          AND EXISTS (
              SELECT 1
              FROM Placement_Drives d
              WHERE d.Drive_ID = j.Drive_ID
                AND d.Company_ID = :2
          )
    """, (
        job_id,
        company_id
    ))

    rows_deleted = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    return rows_deleted
