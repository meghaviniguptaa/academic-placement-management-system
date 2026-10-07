from config.db import get_connection


def get_all_results():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT Round_ID, Application_ID, Result
        FROM Interview_Results
    """)

    columns = [col[0] for col in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return results


def create_result(result):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO Interview_Results
        (Round_ID, Application_ID, Result)
        VALUES
        (:1, :2, :3)
    """, (
        result["Round_ID"],
        result["Application_ID"],
        result["Result"]
    ))

    connection.commit()

    cursor.close()
    connection.close()


def update_result(round_id, application_id, result):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE Interview_Results
        SET Result = :1
        WHERE Round_ID = :2
          AND Application_ID = :3
    """, (
        result["Result"],
        round_id,
        application_id
    ))

    rows_updated = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    return rows_updated


def delete_result(round_id, application_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM Interview_Results
        WHERE Round_ID = :1
          AND Application_ID = :2
    """, (
        round_id,
        application_id
    ))

    rows_deleted = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    return rows_deleted