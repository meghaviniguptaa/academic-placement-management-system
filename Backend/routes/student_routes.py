from flask import Blueprint, jsonify, request, current_app, session
from auth.decorators import roles_required

from controllers.student_controller import (
    get_all_students,
    create_student,
    update_student,
    delete_student,
    get_student_by_id,
    update_own_student_profile
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

# GET - View the logged-in student's own profile
@student_routes.route("/api/student/profile", methods=["GET"])
@roles_required("STUDENT")
def get_my_profile():
    student_id = session.get("student_id")

    if student_id is None:
        return jsonify({"message": "Student account is not linked to a profile."}), 403

    try:
        student = get_student_by_id(student_id)

        if student is None:
            return jsonify({"message": "Student profile not found."}), 404

        return jsonify(student), 200

    except Exception:
        current_app.logger.exception("Fetching student profile failed")
        return jsonify({"message": "Unable to fetch profile."}), 500


# PUT - Update the logged-in student's own profile
@student_routes.route("/api/student/profile", methods=["PUT"])
@roles_required("STUDENT")
def update_my_profile():
    student_id = session.get("student_id")

    if student_id is None:
        return jsonify({"message": "Student account is not linked to a profile."}), 403

    profile = request.get_json(silent=True)

    if not isinstance(profile, dict):
        return jsonify({"message": "A JSON request body is required."}), 400

    required_fields = ["Name", "Email"]

    if any(
        not isinstance(profile.get(field), str) or not profile[field].strip()
        for field in required_fields
    ):
        return jsonify({"message": "Name and Email are required."}), 400

    try:
        rows_updated = update_own_student_profile(student_id, profile)

        if rows_updated == 0:
            return jsonify({"message": "Student profile not found."}), 404

        return jsonify({"message": "Profile updated successfully."}), 200

    except Exception:
        current_app.logger.exception("Updating student profile failed")
        return jsonify({
            "message": "Unable to update profile. Check whether the email is already in use."
        }), 400
