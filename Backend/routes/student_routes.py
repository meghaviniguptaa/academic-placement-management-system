from flask import Blueprint, jsonify, request

from controllers.student_controller import (
    get_all_students,
    create_student,
    update_student,
    delete_student
)


student_routes = Blueprint("student_routes", __name__)


# GET - Read all students
@student_routes.route("/api/students", methods=["GET"])
def get_students():
    students = get_all_students()
    return jsonify(students)


# POST - Create a student
@student_routes.route("/api/students", methods=["POST"])
def add_student():
    student = request.get_json()

    create_student(student)

    return jsonify({
        "message": "Student created successfully"
    }), 201


# PUT - Update a student
@student_routes.route("/api/students/<int:student_id>", methods=["PUT"])
def edit_student(student_id):
    student = request.get_json()

    rows_updated = update_student(student_id, student)

    if rows_updated == 0:
        return jsonify({
            "message": "Student not found"
        }), 404

    return jsonify({
        "message": "Student updated successfully"
    })


# DELETE - Delete a student
@student_routes.route("/api/students/<int:student_id>", methods=["DELETE"])
def remove_student(student_id):
    rows_deleted = delete_student(student_id)

    if rows_deleted == 0:
        return jsonify({
            "message": "Student not found"
        }), 404

    return jsonify({
        "message": "Student deleted successfully"
    })