
from flask import Blueprint, jsonify, request, current_app

from auth.decorators import roles_required

from controllers.result_controller import (
    get_all_results,
    create_result,
    update_result,
    delete_result
)

result_routes = Blueprint("result_routes", __name__)


# GET - Read all interview results (Admin only)
@result_routes.route("/api/interview-results", methods=["GET"])
@roles_required("ADMIN")
def get_results():
    try:
        results = get_all_results()
        return jsonify(results), 200

    except Exception:
        current_app.logger.exception("Fetching interview results failed")
        return jsonify({
            "message": "Unable to fetch interview results."
        }), 500


# POST - Create an interview result (Admin only)
@result_routes.route("/api/interview-results", methods=["POST"])
@roles_required("ADMIN")
def add_result():
    result = request.get_json(silent=True)

    if not isinstance(result, dict):
        return jsonify({
            "message": "A JSON request body is required."
        }), 400

    try:
        create_result(result)

        return jsonify({
            "message": "Interview result created successfully."
        }), 201

    except Exception:
        current_app.logger.exception("Creating interview result failed")
        return jsonify({
            "message": "Unable to create interview result."
        }), 500


# PUT - Update an interview result (Admin only)
@result_routes.route(
    "/api/interview-results/<int:round_id>/<int:application_id>",
    methods=["PUT"]
)
@roles_required("ADMIN")
def edit_result(round_id, application_id):
    result = request.get_json(silent=True)

    if not isinstance(result, dict):
        return jsonify({
            "message": "A JSON request body is required."
        }), 400

    try:
        rows_updated = update_result(
            round_id, application_id, result
        )

        if rows_updated == 0:
            return jsonify({
                "message": "Interview result not found."
            }), 404

        return jsonify({
            "message": "Interview result updated successfully."
        }), 200

    except Exception:
        current_app.logger.exception("Updating interview result failed")
        return jsonify({
            "message": "Unable to update interview result."
        }), 500


# DELETE - Delete an interview result (Admin only)
@result_routes.route(
    "/api/interview-results/<int:round_id>/<int:application_id>",
    methods=["DELETE"]
)
@roles_required("ADMIN")
def remove_result(round_id, application_id):
    try:
        rows_deleted = delete_result(
            round_id, application_id
        )

        if rows_deleted == 0:
            return jsonify({
                "message": "Interview result not found."
            }), 404

        return jsonify({
            "message": "Interview result deleted successfully."
        }), 200

    except Exception:
        current_app.logger.exception("Deleting interview result failed")
        return jsonify({
            "message": "Unable to delete interview result."
        }), 500
