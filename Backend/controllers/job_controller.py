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