from flask import Blueprint, jsonify, request

from controllers.job_controller import (
    get_all_jobs,
    create_job,
    update_job,
    delete_job
)


job_routes = Blueprint("job_routes", __name__)


@job_routes.route("/api/jobs", methods=["GET"])
def get_jobs():
    jobs = get_all_jobs()
    return jsonify(jobs)


@job_routes.route("/api/jobs", methods=["POST"])
def add_job():
    job = request.get_json()

    create_job(job)

    return jsonify({
        "message": "Job posting created successfully"
    }), 201


@job_routes.route("/api/jobs/<int:job_id>", methods=["PUT"])
def edit_job(job_id):
    job = request.get_json()

    rows_updated = update_job(job_id, job)

    if rows_updated == 0:
        return jsonify({
            "message": "Job posting not found"
        }), 404

    return jsonify({
        "message": "Job posting updated successfully"
    })


@job_routes.route("/api/jobs/<int:job_id>", methods=["DELETE"])
def remove_job(job_id):
    rows_deleted = delete_job(job_id)

    if rows_deleted == 0:
        return jsonify({
            "message": "Job posting not found"
        }), 404

    return jsonify({
        "message": "Job posting deleted successfully"
    })