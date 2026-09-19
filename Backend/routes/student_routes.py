from flask import Blueprint, jsonify
from controllers.student_controller import get_all_students

student_routes = Blueprint("student_routes", __name__)


@student_routes.route("/api/students", methods=["GET"])
def get_students():
    students = get_all_students()
    return jsonify(students)