from config.db import get_connection
from auth.passwords import hash_password


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
    connection = None
    cursor = None

    try:
        password = user.get("Password")

        if not isinstance(password, str) or not password:
            raise ValueError("Password is required.")

        password_hash = hash_password(password)

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
            password_hash,
            user["Role"],
            user.get("Student_ID"),
            user.get("Company_ID")
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



def update_user(user_id, user):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Update password only if a new password was provided
        password = user.get("Password")

        if password:
            password_hash = hash_password(password)

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
                password_hash,
                user["Role"],
                user.get("Student_ID"),
                user.get("Company_ID"),
                user_id
            ))

        else:
            # Keep the existing password hash unchanged
            cursor.execute("""
                UPDATE Users
                SET Username = :1,
                    Role = :2,
                    Student_ID = :3,
                    Company_ID = :4
                WHERE User_ID = :5
            """, (
                user["Username"],
                user["Role"],
                user.get("Student_ID"),
                user.get("Company_ID"),
                user_id
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