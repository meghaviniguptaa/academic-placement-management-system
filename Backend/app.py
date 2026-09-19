from flask import Flask, jsonify
from config.db import get_connection

app = Flask(__name__)


@app.route("/")
def home():
    return "Backend is running!"


@app.route("/api/students", methods=["GET"])
def get_students():
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

    return jsonify(students)


if __name__ == "__main__":
    app.run(debug=True)