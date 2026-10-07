from config.db import get_connection


def get_all_interview_rounds():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT Round_ID, Job_ID, Round_Number, Round_Type
        FROM Interview_Rounds
    """)

    columns = [col[0] for col in cursor.description]
    rounds = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return rounds


def create_interview_round(round_data):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO Interview_Rounds
        (Round_ID, Job_ID, Round_Number, Round_Type)
        VALUES
        (:1, :2, :3, :4)
    """, (
        round_data["Round_ID"],
        round_data["Job_ID"],
        round_data["Round_Number"],
        round_data["Round_Type"]
    ))

    connection.commit()

    cursor.close()
    connection.close()


def update_interview_round(round_id, round_data):
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

    cursor.close()
    connection.close()

    return rows_updated


def delete_interview_round(round_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM Interview_Rounds
        WHERE Round_ID = :1
    """, (round_id,))

    rows_deleted = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    return rows_deleted