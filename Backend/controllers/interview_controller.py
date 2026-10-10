
from config.db import get_connection


# --------------------------------------------------
# GET ALL INTERVIEW ROUNDS (existing CRUD)
# --------------------------------------------------
def get_all_interview_rounds():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT Round_ID, Job_ID, Round_Number, Round_Type
            FROM Interview_Rounds
            ORDER BY Job_ID, Round_Number
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
# CREATE INTERVIEW ROUND (existing CRUD)
# --------------------------------------------------
def create_interview_round(round_data):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO Interview_Rounds
                (Round_ID, Job_ID, Round_Number, Round_Type)
            VALUES (:1, :2, :3, :4)
        """, (
            round_data["Round_ID"],
            round_data["Job_ID"],
            round_data["Round_Number"],
            round_data["Round_Type"]
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
# UPDATE INTERVIEW ROUND (existing CRUD)
# --------------------------------------------------
def update_interview_round(round_id, round_data):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE Interview_Rounds
            SET Job_ID = :1,
                Round_Number = :2,
                Round_Type = :3
            WHERE Round_ID = :4
        """, (
            round_data["Job_ID"],
            round_data["Round_Number"],
            round_data["Round_Type"],
            round_id
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
# DELETE INTERVIEW ROUND (existing CRUD)
# --------------------------------------------------
def delete_interview_round(round_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM Interview_Rounds
            WHERE Round_ID = :1
        """, (round_id,))

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
# GET INTERVIEW ROUNDS AND RESULTS FOR ONE STUDENT
# --------------------------------------------------
def get_my_interview_results(student_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                a.Application_ID,
                j.Job_ID,
                j.Job_Title,
                c.Company_Name,
                ir.Round_ID,
                ir.Round_Number,
                ir.Round_Type,
                NVL(res.Result, 'PENDING') AS Result
            FROM Applications a
            JOIN Job_Postings j
                ON a.Job_ID = j.Job_ID
            JOIN Placement_Drives d
                ON j.Drive_ID = d.Drive_ID
            JOIN Companies c
                ON d.Company_ID = c.Company_ID
            JOIN Interview_Rounds ir
                ON ir.Job_ID = a.Job_ID
            LEFT JOIN Interview_Results res
                ON res.Round_ID = ir.Round_ID
               AND res.Application_ID = a.Application_ID
            WHERE a.Student_ID = :1
            ORDER BY
                a.Application_ID,
                ir.Round_Number
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
