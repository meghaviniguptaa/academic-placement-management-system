from config.db import get_connection


def get_all_users():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT User_ID, Username, Role, Student_ID, Company_ID
        FROM Users
    """)

    columns = [col[0] for col in cursor.description]
    users = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return users


def create_user(user):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO Users
        (User_ID, Username, Password_Hash, Role,
         Student_ID, Company_ID)
        VALUES
        (:1, :2, :3, :4, :5, :6)
    """, (
        user["User_ID"],
        user["Username"],
        user["Password_Hash"],
        user["Role"],
        user.get("Student_ID"),
        user.get("Company_ID")
    ))

    connection.commit()

    cursor.close()
    connection.close()


def update_user(user_id, user):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE Users
        SET Username = :1,
            Password_Hash = :2,
            Role = :3,
            Student_ID = :4,
            Company_ID = :5
        WHERE User_ID = :6
    """, (
        user["Username"],
        user["Password_Hash"],
        user["Role"],
        user.get("Student_ID"),
        user.get("Company_ID"),
        user_id
    ))

    rows_updated = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    return rows_updated


def delete_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM Users
        WHERE User_ID = :1
    """, (user_id,))

    rows_deleted = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    return rows_deleted