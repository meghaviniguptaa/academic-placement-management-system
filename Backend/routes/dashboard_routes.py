
from flask import Blueprint, jsonify, current_app, session

from auth.decorators import roles_required
from utils.validation import is_positive_int
from controllers.dashboard_controller import get_student_dashboard

dashboard_routes = Blueprint("dashboard_routes", __name__)


# GET - Student dashboard statistics
@dashboard_routes.route("/api/student/dashboard", methods=["GET"])
@roles_required("STUDENT")
def student_dashboard():
    student_id = session.get("student_id")

    if not is_positive_int(student_id):
        return jsonify({
            "message": "Student account is not linked to a profile."
        }), 403

    try:
        dashboard = get_student_dashboard(student_id)
        return jsonify(dashboard), 200

    except Exception:
        current_app.logger.exception(
            "Fetching student dashboard failed"
        )
        return jsonify({
            "message": "Unable to fetch dashboard."
        }), 500
