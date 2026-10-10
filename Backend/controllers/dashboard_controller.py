
from config.db import get_connection


def get_student_dashboard(student_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                (SELECT COUNT(*)
                 FROM Applications
                 WHERE Student_ID = :student_id)
                    AS TOTAL_APPLICATIONS,

                (SELECT COUNT(*)
                 FROM Applications
                 WHERE Student_ID = :student_id
                   AND Status = 'SHORTLISTED')
                    AS SHORTLISTED_APPLICATIONS,

                (SELECT COUNT(*)
                 FROM Applications a
                 JOIN Interview_Results r
                   ON r.Application_ID = a.Application_ID
                 WHERE a.Student_ID = :student_id
                   AND r.Result = 'PASSED')
                    AS PASSED_ROUNDS,

                (SELECT COUNT(*)
                 FROM Offers o
                 JOIN Applications a
                   ON a.Application_ID = o.Application_ID
                 WHERE a.Student_ID = :student_id)
                    AS TOTAL_OFFERS,

                (SELECT COUNT(*)
                 FROM Offers o
                 JOIN Applications a
                   ON a.Application_ID = o.Application_ID
                 WHERE a.Student_ID = :student_id
                   AND o.Offer_Status = 'ACCEPTED')
                    AS ACCEPTED_OFFERS

            FROM DUAL
        """, {"student_id": student_id})

        row = cursor.fetchone()
        columns = [col[0] for col in cursor.description]

        return dict(zip(columns, row))

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
