from config.db import get_connection


def get_all_drives():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT Drive_ID, Company_ID, Drive_Date, Venue, Drive_Status
        FROM Placement_Drives
    """)

    columns = [col[0] for col in cursor.description]
    drives = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return drives


def create_drive(drive):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO Placement_Drives
        (Drive_ID, Company_ID, Drive_Date, Venue, Drive_Status)
        VALUES
        (:1, :2, :3, :4, :5)
    """, (
        drive["Drive_ID"],
        drive["Company_ID"],
        drive["Drive_Date"],
        drive["Venue"],
        drive["Drive_Status"]
    ))

    connection.commit()

    cursor.close()
    connection.close()


def update_drive(drive_id, drive):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE Placement_Drives
        SET Company_ID = :1,
            Drive_Date = :2,
            Venue = :3,
            Drive_Status = :4
        WHERE Drive_ID = :5
    """, (
        drive["Company_ID"],
        drive["Drive_Date"],
        drive["Venue"],
        drive["Drive_Status"],
        drive_id
    ))

    rows_updated = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    return rows_updated


def delete_drive(drive_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM Placement_Drives
        WHERE Drive_ID = :1
    """, (drive_id,))

    rows_deleted = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    return rows_deleted