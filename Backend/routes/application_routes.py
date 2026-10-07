from flask import Blueprint, jsonify, request

from controllers.application_controller import (
    get_all_applications,
    create_application,
    update_application,
    delete_application
)

application_routes = Blueprint("application_routes", __name__)


# GET - Read all applications
@application_routes.route("/api/applications", methods=["GET"])
def get_applications():
    applications = get_all_applications()
    return jsonify(applications)


# POST - Create an application
@application_routes.route("/api/applications", methods=["POST"])
def add_application():
    application = request.get_json()
    create_application(application)

    return jsonify({
        "message": "Application created successfully"
    }), 201


# PUT - Update an application
@application_routes.route("/api/applications/<int:application_id>", methods=["PUT"])
def edit_application(application_id):
    application = request.get_json()
    rows_updated = update_application(application_id, application)

    if rows_updated == 0:
        return jsonify({
            "message": "Application not found"
        }), 404

    return jsonify({
        "message": "Application updated successfully"
    })


# DELETE - Delete an application
@application_routes.route("/api/applications/<int:application_id>", methods=["DELETE"])
def remove_application(application_id):
    rows_deleted = delete_application(application_id)

    if rows_deleted == 0:
        return jsonify({
            "message": "Application not found"
        }), 404

    return jsonify({
        "message": "Application deleted successfully"
    })