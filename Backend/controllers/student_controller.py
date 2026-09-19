from config.db import get_connection


def get_all_students():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT Student_ID, Name, Email, Phone, Department,
               CGPA, Graduation_Year, Resume_URL
        FROM Students
    """)

    columns = [col[0] for col in cursor.description]
    students = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return students