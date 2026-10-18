
from flask import Blueprint, jsonify, request, current_app, session

from auth.decorators import roles_required
from utils.validation import is_positive_int

from controllers.interview_controller import (
    get_all_interview_rounds,
    create_interview_round,
    update_interview_round,
    delete_interview_round,
    get_my_interview_results,
    get_company_interview_rounds,
    create_company_interview_round,
    update_company_interview_round,
    delete_company_interview_round
)

interview_routes = Blueprint("interview_routes", __name__)


@interview_routes.route("/api/interview-rounds", methods=["GET"])
@roles_required("ADMIN")
def get_interview_rounds():
    try:
        rounds = get_all_interview_rounds()
        return jsonify(rounds), 200

    except Exception:
        current_app.logger.exception("Fetching interview rounds failed")
        return jsonify({
            "message": "Unable to fetch interview rounds."
        }), 500


# --------------------------------------------------
# POST - Create an interview round (existing CRUD)
# --------------------------------------------------
@interview_routes.route("/api/interview-rounds", methods=["POST"])
@roles_required("ADMIN")
def add_interview_round():
    round_data = request.get_json(silent=True)

    if not isinstance(round_data, dict):
        return jsonify({
            "message": "A JSON request body is required."
        }), 400

    try:
        create_interview_round(round_data)

        return jsonify({
            "message": "Interview round created successfully."
        }), 201

    except Exception:
        current_app.logger.exception("Creating interview round failed")
        return jsonify({
            "message": "Unable to create interview round."
        }), 500


# --------------------------------------------------
# PUT - Update an interview round (existing CRUD)
# --------------------------------------------------
@interview_routes.route(
    "/api/interview-rounds/<int:round_id>",
    methods=["PUT"]
)
@roles_required("ADMIN")
def edit_interview_round(round_id):
    round_data = request.get_json(silent=True)

    if not isinstance(round_data, dict):
        return jsonify({
            "message": "A JSON request body is required."
        }), 400

    try:
        rows_updated = update_interview_round(
            round_id, round_data
        )

        if rows_updated == 0:
            return jsonify({
                "message": "Interview round not found."
            }), 404

        return jsonify({
            "message": "Interview round updated successfully."
        }), 200

    except Exception:
        current_app.logger.exception("Updating interview round failed")
        return jsonify({
            "message": "Unable to update interview round."
        }), 500


# --------------------------------------------------
# DELETE - Delete an interview round (existing CRUD)
# --------------------------------------------------
@interview_routes.route(
    "/api/interview-rounds/<int:round_id>",
    methods=["DELETE"]
)
@roles_required("ADMIN")
def remove_interview_round(round_id):
    try:
        rows_deleted = delete_interview_round(round_id)

        if rows_deleted == 0:
            return jsonify({
                "message": "Interview round not found."
            }), 404

        return jsonify({
            "message": "Interview round deleted successfully."
        }), 200

    except Exception:
        current_app.logger.exception("Deleting interview round failed")
        return jsonify({
            "message": "Unable to delete interview round."
        }), 500


# --------------------------------------------------
# GET - View the logged-in student's interview results
# --------------------------------------------------
@interview_routes.route(
    "/api/student/interview-results",
    methods=["GET"]
)
@roles_required("STUDENT")
def student_interview_results():
    student_id = session.get("student_id")

    if not is_positive_int(student_id):
        return jsonify({
            "message": "Student account is not linked to a profile."
        }), 403

    try:
        results = get_my_interview_results(student_id)
        return jsonify(results), 200

    except Exception:
        current_app.logger.exception(
            "Fetching student interview results failed"
        )
        return jsonify({
            "message": "Unable to fetch interview results."
        }), 500

# --------------------------------------------------
# RECRUITER INTERVIEW ROUND MANAGEMENT
# --------------------------------------------------

@interview_routes.route(
    "/api/recruiter/interview-rounds",
    methods=["GET"]
)
@roles_required("RECRUITER")
def get_recruiter_interview_rounds():
    company_id = session.get("company_id")

    if not is_positive_int(company_id):
        return jsonify({
            "message": "Recruiter account is not linked to a company."
        }), 403

    try:
        rounds = get_company_interview_rounds(company_id)
        return jsonify(rounds), 200

    except Exception:
        current_app.logger.exception(
            "Fetching recruiter interview rounds failed"
        )
        return jsonify({
            "message": "Unable to fetch interview rounds."
        }), 500


@interview_routes.route(
    "/api/recruiter/interview-rounds",
    methods=["POST"]
)
@roles_required("RECRUITER")
def add_recruiter_interview_round():
    company_id = session.get("company_id")

    if not is_positive_int(company_id):
        return jsonify({
            "message": "Recruiter account is not linked to a company."
        }), 403

    round_data = request.get_json(silent=True)

    if not isinstance(round_data, dict):
        return jsonify({
            "message": "A JSON request body is required."
        }), 400

    try:
        create_company_interview_round(
            company_id,
            round_data
        )

        return jsonify({
            "message": "Interview round created successfully."
        }), 201

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400

    except Exception:
        current_app.logger.exception(
            "Creating recruiter interview round failed"
        )
        return jsonify({
            "message": "Unable to create interview round."
        }), 500


@interview_routes.route(
    "/api/recruiter/interview-rounds/<int:round_id>",
    methods=["PUT"]
)
@roles_required("RECRUITER")
def edit_recruiter_interview_round(round_id):
    company_id = session.get("company_id")

    if not is_positive_int(company_id):
        return jsonify({
            "message": "Recruiter account is not linked to a company."
        }), 403

    round_data = request.get_json(silent=True)

    if not isinstance(round_data, dict):
        return jsonify({
            "message": "A JSON request body is required."
        }), 400

    try:
        rows_updated = update_company_interview_round(
            company_id,
            round_id,
            round_data
        )

        if rows_updated == 0:
            return jsonify({
                "message": "Interview round not found for your company."
            }), 404

        return jsonify({
            "message": "Interview round updated successfully."
        }), 200

    except Exception:
        current_app.logger.exception(
            "Updating recruiter interview round failed"
        )
        return jsonify({
            "message": "Unable to update interview round."
        }), 500


@interview_routes.route(
    "/api/recruiter/interview-rounds/<int:round_id>",
    methods=["DELETE"]
)
@roles_required("RECRUITER")
def remove_recruiter_interview_round(round_id):
    company_id = session.get("company_id")

    if not is_positive_int(company_id):
        return jsonify({
            "message": "Recruiter account is not linked to a company."
        }), 403

    try:
        rows_deleted = delete_company_interview_round(
            company_id,
            round_id
        )

        if rows_deleted == 0:
            return jsonify({
                "message": "Interview round not found for your company."
            }), 404

        return jsonify({
            "message": "Interview round deleted successfully."
        }), 200

    except Exception:
        current_app.logger.exception(
            "Deleting recruiter interview round failed"
        )
        return jsonify({
            "message": "Unable to delete interview round."
        }), 500