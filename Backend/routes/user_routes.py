
from flask import Blueprint, jsonify, request, current_app

from auth.decorators import roles_required

from controllers.user_controller import (
    get_all_users,
    create_user,
    update_user,
    delete_user
)

user_routes = Blueprint("user_routes", __name__)


# --------------------------------------------------
# GET - Read all users (Admin only)
# --------------------------------------------------
@user_routes.route("/api/users", methods=["GET"])
@roles_required("ADMIN")
def get_users():
    try:
        users = get_all_users()
        return jsonify(users), 200

    except Exception:
        current_app.logger.exception("Fetching users failed")
        return jsonify({
            "message": "Unable to fetch users."
        }), 500


# --------------------------------------------------
# POST - Create a user (Admin only)
# --------------------------------------------------
@user_routes.route("/api/users", methods=["POST"])
@roles_required("ADMIN")
def add_user():
    user = request.get_json(silent=True)

    if not isinstance(user, dict):
        return jsonify({
            "message": "A JSON request body is required."
        }), 400

    required = ["User_ID", "Username", "Password", "Role"]

    if any(
        not user.get(field)
        or (
            isinstance(user.get(field), str)
            and not user[field].strip()
        )
        for field in required
    ):
        return jsonify({
            "message": "User_ID, Username, Password and Role are required."
        }), 400

    try:
        create_user(user)

        return jsonify({
            "message": "User created successfully."
        }), 201

    except Exception:
        current_app.logger.exception("User creation failed")
        return jsonify({
            "message": "Unable to create user."
        }), 400


# --------------------------------------------------
# PUT - Update a user (Admin only)
# --------------------------------------------------
@user_routes.route("/api/users/<int:user_id>", methods=["PUT"])
@roles_required("ADMIN")
def edit_user(user_id):
    user = request.get_json(silent=True)

    if not isinstance(user, dict):
        return jsonify({
            "message": "A JSON request body is required."
        }), 400

    try:
        rows_updated = update_user(user_id, user)

        if rows_updated == 0:
            return jsonify({
                "message": "User not found."
            }), 404

        return jsonify({
            "message": "User updated successfully."
        }), 200

    except Exception:
        current_app.logger.exception("User update failed")
        return jsonify({
            "message": "Unable to update user."
        }), 400


# --------------------------------------------------
# DELETE - Delete a user (Admin only)
# --------------------------------------------------
@user_routes.route("/api/users/<int:user_id>", methods=["DELETE"])
@roles_required("ADMIN")
def remove_user(user_id):
    try:
        rows_deleted = delete_user(user_id)

        if rows_deleted == 0:
            return jsonify({
                "message": "User not found."
            }), 404

        return jsonify({
            "message": "User deleted successfully."
        }), 200

    except Exception:
        current_app.logger.exception("User deletion failed")
        return jsonify({
            "message": "Unable to delete user."
        }), 400
