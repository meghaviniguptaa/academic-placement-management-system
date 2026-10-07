from flask import Blueprint, jsonify, request

from controllers.user_controller import (
    get_all_users,
    create_user,
    update_user,
    delete_user
)

user_routes = Blueprint("user_routes", __name__)


@user_routes.route("/api/users", methods=["GET"])
def get_users():
    users = get_all_users()
    return jsonify(users)


@user_routes.route("/api/users", methods=["POST"])
def add_user():
    user = request.get_json()
    create_user(user)

    return jsonify({
        "message": "User created successfully"
    }), 201


@user_routes.route("/api/users/<int:user_id>", methods=["PUT"])
def edit_user(user_id):
    user = request.get_json()
    rows_updated = update_user(user_id, user)

    if rows_updated == 0:
        return jsonify({
            "message": "User not found"
        }), 404

    return jsonify({
        "message": "User updated successfully"
    })


@user_routes.route("/api/users/<int:user_id>", methods=["DELETE"])
def remove_user(user_id):
    rows_deleted = delete_user(user_id)

    if rows_deleted == 0:
        return jsonify({
            "message": "User not found"
        }), 404

    return jsonify({
        "message": "User deleted successfully"
    })