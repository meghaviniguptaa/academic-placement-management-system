from flask import Blueprint, jsonify, request

from controllers.result_controller import (
    get_all_results,
    create_result,
    update_result,
    delete_result
)

result_routes = Blueprint("result_routes", __name__)


@result_routes.route("/api/interview-results", methods=["GET"])
def get_results():
    results = get_all_results()
    return jsonify(results)


@result_routes.route("/api/interview-results", methods=["POST"])
def add_result():
    result = request.get_json()
    create_result(result)

    return jsonify({
        "message": "Interview result created successfully"
    }), 201


@result_routes.route(
    "/api/interview-results/<int:round_id>/<int:application_id>",
    methods=["PUT"]
)
def edit_result(round_id, application_id):
    result = request.get_json()

    rows_updated = update_result(
        round_id,
        application_id,
        result
    )

    if rows_updated == 0:
        return jsonify({
            "message": "Interview result not found"
        }), 404

    return jsonify({
        "message": "Interview result updated successfully"
    })


@result_routes.route(
    "/api/interview-results/<int:round_id>/<int:application_id>",
    methods=["DELETE"]
)
def remove_result(round_id, application_id):
    rows_deleted = delete_result(
        round_id,
        application_id
    )

    if rows_deleted == 0:
        return jsonify({
            "message": "Interview result not found"
        }), 404

    return jsonify({
        "message": "Interview result deleted successfully"
    })