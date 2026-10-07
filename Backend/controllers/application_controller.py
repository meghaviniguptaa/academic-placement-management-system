from config.db import get_connection


def get_all_applications():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT Application_ID, Student_ID, Job_ID,
               Application_Date, Status
        FROM Applications
    """)

    columns = [col[0] for col in cursor.description]
    applications = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return applications


def create_application(application):
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

    cursor.close()
    connection.close()


def update_application(application_id, application):
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

    cursor.close()
    connection.close()

    return rows_updated


def delete_application(application_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM Applications
        WHERE Application_ID = :1
    """, (application_id,))

    rows_deleted = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    return rows_deleted