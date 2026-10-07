from flask import Blueprint, jsonify, request
from controllers.student_controller import get_all_students, create_student

student_routes = Blueprint("student_routes", __name__)


@student_routes.route("/api/students", methods=["GET"])
def get_students():
    students = get_all_students()
    return jsonify(students)


@student_routes.route("/api/students", methods=["POST"])
def add_student():
    student = request.get_json()
    create_student(student)
    return jsonify({"message": "Student created successfully"}), 201