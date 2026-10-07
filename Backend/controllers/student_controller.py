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


def create_student(student):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO Students
        (Student_ID, Name, Email, Phone, Department,
         CGPA, Graduation_Year, Resume_URL)
        VALUES
        (:1, :2, :3, :4, :5, :6, :7, :8)
    """, (
        student["Student_ID"],
        student["Name"],
        student["Email"],
        student["Phone"],
        student["Department"],
        student["CGPA"],
        student["Graduation_Year"],
        student["Resume_URL"]
    ))

    connection.commit()

    cursor.close()
    connection.close()


def update_student(student_id, student):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE Students
        SET Name = :1,
            Email = :2,
            Phone = :3,
            Department = :4,
            CGPA = :5,
            Graduation_Year = :6,
            Resume_URL = :7
        WHERE Student_ID = :8
    """, (
        student["Name"],
        student["Email"],
        student["Phone"],
        student["Department"],
        student["CGPA"],
        student["Graduation_Year"],
        student["Resume_URL"],
        student_id
    ))

    rows_updated = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    return rows_updated


def delete_student(student_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM Students
        WHERE Student_ID = :1
    """, (student_id,))

    rows_deleted = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    return rows_deleted