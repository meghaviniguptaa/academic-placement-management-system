
from flask import Blueprint, jsonify, request, session, current_app
from config.db import get_connection
from auth.passwords import verify_password

auth_routes = Blueprint("auth_routes", __name__)

@auth_routes.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "message": "A JSON request body is required."
        }), 400

    username = data.get("Username")
    password = data.get("Password")

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({
            "message": "Username and password are required."
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT User_ID, Username, Password_Hash,
                   Role, Student_ID, Company_ID
            FROM Users
            WHERE Username = :username
        """, {"username": username})

        user = cursor.fetchone()

        if not user or not verify_password(password, user[2]):
            return jsonify({
                "message": "Invalid username or password."
            }), 401

        # Start a fresh session after successful verification.
        session.clear()
        session["user_id"] = user[0]
        session["username"] = user[1]
        session["role"] = user[3]
        session["student_id"] = user[4]
        session["company_id"] = user[5]

        return jsonify({
            "message": "Login successful.",
            "user": {
                "User_ID": user[0],
                "Username": user[1],
                "Role": user[3],
                "Student_ID": user[4],
                "Company_ID": user[5]
            }
        }), 200

    except Exception:
        current_app.logger.exception("Authentication error")
        return jsonify({
            "message": "Unable to complete login."
        }), 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


@auth_routes.route("/api/auth/me", methods=["GET"])
def current_user():
    if "user_id" not in session:
        return jsonify({
            "message": "Authentication required."
        }), 401

    return jsonify({
        "user_id": session["user_id"],
        "username": session["username"],
        "role": session["role"],
        "student_id": session.get("student_id"),
        "company_id": session.get("company_id")
    }), 200


@auth_routes.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "message": "Logged out successfully."
    }), 200
