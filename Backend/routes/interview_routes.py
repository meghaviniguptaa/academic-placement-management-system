from flask import Blueprint, jsonify, request

from controllers.interview_controller import (
    get_all_interview_rounds,
    create_interview_round,
    update_interview_round,
    delete_interview_round
)

interview_routes = Blueprint("interview_routes", __name__)


@interview_routes.route("/api/interview-rounds", methods=["GET"])
def get_interview_rounds():
    rounds = get_all_interview_rounds()
    return jsonify(rounds)


@interview_routes.route("/api/interview-rounds", methods=["POST"])
def add_interview_round():
    round_data = request.get_json()
    create_interview_round(round_data)

    return jsonify({
        "message": "Interview round created successfully"
    }), 201


@interview_routes.route("/api/interview-rounds/<int:round_id>", methods=["PUT"])
def edit_interview_round(round_id):
    round_data = request.get_json()
    rows_updated = update_interview_round(round_id, round_data)

    if rows_updated == 0:
        return jsonify({
            "message": "Interview round not found"
        }), 404

    return jsonify({
        "message": "Interview round updated successfully"
    })


@interview_routes.route("/api/interview-rounds/<int:round_id>", methods=["DELETE"])
def remove_interview_round(round_id):
    rows_deleted = delete_interview_round(round_id)

    if rows_deleted == 0:
        return jsonify({
            "message": "Interview round not found"
        }), 404

    return jsonify({
        "message": "Interview round deleted successfully"
    })