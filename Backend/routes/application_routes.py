from flask import Blueprint, jsonify, request, current_app, session

from auth.decorators import roles_required
from utils.validation import is_positive_int

from controllers.application_controller import (
    get_all_applications,
    create_application,
    update_application,
    delete_application,
    get_my_applications,
    apply_for_job
)

application_routes = Blueprint("application_routes", __name__)


@application_routes.route("/api/applications", methods=["GET"])
@roles_required("ADMIN")
def get_applications():
    try:
        applications = get_all_applications()
        return jsonify(applications), 200

    except Exception:
        current_app.logger.exception("Fetching applications failed")
        return jsonify({
            "message": "Unable to fetch applications."
        }), 500


@application_routes.route("/api/applications", methods=["POST"])
@roles_required("ADMIN")
def add_application():
    application = request.get_json(silent=True)

    if not isinstance(application, dict):
        return jsonify({
            "message": "A JSON request body is required."
        }), 400

    try:
        create_application(application)

        return jsonify({
            "message": "Application created successfully."
        }), 201

    except Exception:
        current_app.logger.exception("Creating application failed")
        return jsonify({
            "message": "Unable to create application."
        }), 500


@application_routes.route("/api/applications/<int:application_id>", methods=["PUT"])
@roles_required("ADMIN")
def edit_application(application_id):
    application = request.get_json(silent=True)

    if not isinstance(application, dict):
        return jsonify({
            "message": "A JSON request body is required."
        }), 400

    try:
        rows_updated = update_application(
            application_id, application
        )

        if rows_updated == 0:
            return jsonify({
                "message": "Application not found."
            }), 404

        return jsonify({
            "message": "Application updated successfully."
        }), 200

    except Exception:
        current_app.logger.exception("Updating application failed")
        return jsonify({
            "message": "Unable to update application."
        }), 500


@application_routes.route("/api/applications/<int:application_id>", methods=["DELETE"])
@roles_required("ADMIN")
def remove_application(application_id):
    try:
        rows_deleted = delete_application(application_id)

        if rows_deleted == 0:
            return jsonify({
                "message": "Application not found."
            }), 404

        return jsonify({
            "message": "Application deleted successfully."
        }), 200

    except Exception:
        current_app.logger.exception("Deleting application failed")
        return jsonify({
            "message": "Unable to delete application."
        }), 500


# --------------------------------------------------
# GET - View the logged-in student's applications
# --------------------------------------------------
@application_routes.route(
    "/api/student/applications",
    methods=["GET"]
)
@roles_required("STUDENT")
def get_student_applications():
    student_id = session.get("student_id")

    if not is_positive_int(student_id):
        return jsonify({
            "message": "Student account is not linked to a profile."
        }), 403

    try:
        applications = get_my_applications(student_id)
        return jsonify(applications), 200

    except Exception:
        current_app.logger.exception(
            "Fetching student applications failed"
        )
        return jsonify({
            "message": "Unable to fetch applications."
        }), 500


# --------------------------------------------------
# POST - Apply for a job as the logged-in student
# --------------------------------------------------
@application_routes.route(
    "/api/student/applications",
    methods=["POST"]
)
@roles_required("STUDENT")
def student_apply_for_job():
    student_id = session.get("student_id")

    if not is_positive_int(student_id):
        return jsonify({
            "message": "Student account is not linked to a profile."
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "message": "A JSON request body is required."
        }), 400

    job_id = data.get("Job_ID")

    if not is_positive_int(job_id):
        return jsonify({
            "message": "A valid Job_ID is required."
        }), 400

    try:
        result, status_code = apply_for_job(
            student_id, job_id
        )

        return jsonify(result), status_code

    except Exception:
        current_app.logger.exception("Job application failed")
        return jsonify({
            "message": "Unable to submit application."
        }), 500
