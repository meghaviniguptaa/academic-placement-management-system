
from flask import Blueprint, jsonify, request, current_app, session
from utils.validation import is_positive_int
from auth.decorators import roles_required

from controllers.job_controller import (
    get_all_jobs,
    create_job,
    update_job,
    delete_job,
    get_student_jobs,
    get_student_job_details
)

job_routes = Blueprint("job_routes", __name__)


# --------------------------------------------------
# GET - Read all job postings (Admin only)
# --------------------------------------------------
@job_routes.route("/api/jobs", methods=["GET"])
@roles_required("ADMIN")
def get_jobs():
    try:
        jobs = get_all_jobs()
        return jsonify(jobs), 200

    except Exception:
        current_app.logger.exception("Fetching jobs failed")
        return jsonify({
            "message": "Unable to fetch job postings."
        }), 500


# --------------------------------------------------
# POST - Create a job posting (Admin only)
# --------------------------------------------------
@job_routes.route("/api/jobs", methods=["POST"])
@roles_required("ADMIN")
def add_job():
    job = request.get_json(silent=True)

    if not isinstance(job, dict):
        return jsonify({
            "message": "A JSON request body is required."
        }), 400

    try:
        create_job(job)

        return jsonify({
            "message": "Job posting created successfully."
        }), 201

    except Exception:
        current_app.logger.exception("Creating job posting failed")
        return jsonify({
            "message": "Unable to create job posting."
        }), 500


# --------------------------------------------------
# PUT - Update a job posting (Admin only)
# --------------------------------------------------
@job_routes.route("/api/jobs/<int:job_id>", methods=["PUT"])
@roles_required("ADMIN")
def edit_job(job_id):
    job = request.get_json(silent=True)

    if not isinstance(job, dict):
        return jsonify({
            "message": "A JSON request body is required."
        }), 400

    try:
        rows_updated = update_job(job_id, job)

        if rows_updated == 0:
            return jsonify({
                "message": "Job posting not found."
            }), 404

        return jsonify({
            "message": "Job posting updated successfully."
        }), 200

    except Exception:
        current_app.logger.exception("Updating job posting failed")
        return jsonify({
            "message": "Unable to update job posting."
        }), 500


# --------------------------------------------------
# DELETE - Delete a job posting (Admin only)
# --------------------------------------------------
@job_routes.route("/api/jobs/<int:job_id>", methods=["DELETE"])
@roles_required("ADMIN")
def remove_job(job_id):
    try:
        rows_deleted = delete_job(job_id)

        if rows_deleted == 0:
            return jsonify({
                "message": "Job posting not found."
            }), 404

        return jsonify({
            "message": "Job posting deleted successfully."
        }), 200

    except Exception:
        current_app.logger.exception("Deleting job posting failed")
        return jsonify({
            "message": "Unable to delete job posting."
        }), 500

# GET - Browse available jobs as a Student
@job_routes.route("/api/student/jobs", methods=["GET"])
@roles_required("STUDENT")
def browse_student_jobs():
    search = request.args.get("search")
    min_package = request.args.get("min_package")
    max_package = request.args.get("max_package")

    try:
        if min_package is not None:
            min_package = float(min_package)
            if min_package < 0:
                raise ValueError()

        if max_package is not None:
            max_package = float(max_package)
            if max_package < 0:
                raise ValueError()

        if (
            min_package is not None
            and max_package is not None
            and min_package > max_package
        ):
            return jsonify({
                "message": "Minimum package cannot exceed maximum package."
            }), 400

        jobs = get_student_jobs(
            search=search,
            min_package=min_package,
            max_package=max_package
        )

        return jsonify(jobs), 200

    except ValueError:
        return jsonify({
            "message": "Package filters must be valid non-negative numbers."
        }), 400

    except Exception:
        current_app.logger.exception("Fetching student jobs failed")
        return jsonify({
            "message": "Unable to fetch available jobs."
        }), 500


# GET - View details of one available job
@job_routes.route("/api/student/jobs/<int:job_id>", methods=["GET"])
@roles_required("STUDENT")
def student_job_details(job_id):
    try:
        job = get_student_job_details(job_id)

        if not job:
            return jsonify({
                "message": "Job not found or no longer available."
            }), 404

        return jsonify(job), 200

    except Exception:
        current_app.logger.exception("Fetching job details failed")
        return jsonify({
            "message": "Unable to fetch job details."
        }), 500