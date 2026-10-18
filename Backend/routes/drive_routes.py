from flask import Blueprint, jsonify, request, session
from auth.decorators import roles_required

from controllers.drive_controller import (
    get_all_drives,
    create_drive,
    update_drive,
    delete_drive,
    get_company_drives,
    create_company_drive,
    update_company_drive,
    delete_company_drive
)


drive_routes = Blueprint("drive_routes", __name__)


@drive_routes.route("/api/drives", methods=["GET"])
@roles_required("ADMIN")
def get_drives():
    drives = get_all_drives()
    return jsonify(drives)


@drive_routes.route("/api/drives", methods=["POST"])
@roles_required("ADMIN")
def add_drive():
    drive = request.get_json()

    create_drive(drive)

    return jsonify({
        "message": "Placement drive created successfully"
    }), 201


@drive_routes.route("/api/drives/<int:drive_id>", methods=["PUT"])
@roles_required("ADMIN")
def edit_drive(drive_id):
    drive = request.get_json()

    rows_updated = update_drive(drive_id, drive)

    if rows_updated == 0:
        return jsonify({
            "message": "Placement drive not found"
        }), 404

    return jsonify({
        "message": "Placement drive updated successfully"
    })


@drive_routes.route("/api/drives/<int:drive_id>", methods=["DELETE"])
@roles_required("ADMIN")
def remove_drive(drive_id):
    rows_deleted = delete_drive(drive_id)

    if rows_deleted == 0:
        return jsonify({
            "message": "Placement drive not found"
        }), 404

    return jsonify({
        "message": "Placement drive deleted successfully"
    })

@drive_routes.route("/api/recruiter/drives", methods=["GET"])
@roles_required("RECRUITER")
def get_recruiter_drives():
    company_id = session.get("company_id")

    if not company_id:
        return jsonify({
            "message": "No company is associated with this recruiter."
        }), 400

    drives = get_company_drives(company_id)

    return jsonify(drives), 200


@drive_routes.route("/api/recruiter/drives", methods=["POST"])
@roles_required("RECRUITER")
def add_recruiter_drive():
    company_id = session.get("company_id")

    if not company_id:
        return jsonify({
            "message": "No company is associated with this recruiter."
        }), 400

    drive = request.get_json()

    create_company_drive(company_id, drive)

    return jsonify({
        "message": "Placement drive created successfully"
    }), 201


@drive_routes.route("/api/recruiter/drives/<int:drive_id>", methods=["PUT"])
@roles_required("RECRUITER")
def edit_recruiter_drive(drive_id):
    company_id = session.get("company_id")

    if not company_id:
        return jsonify({
            "message": "No company is associated with this recruiter."
        }), 400

    drive = request.get_json()

    rows_updated = update_company_drive(
        company_id,
        drive_id,
        drive
    )

    if rows_updated == 0:
        return jsonify({
            "message": "Placement drive not found for your company."
        }), 404

    return jsonify({
        "message": "Placement drive updated successfully"
    }), 200


@drive_routes.route("/api/recruiter/drives/<int:drive_id>", methods=["DELETE"])
@roles_required("RECRUITER")
def remove_recruiter_drive(drive_id):
    company_id = session.get("company_id")

    if not company_id:
        return jsonify({
            "message": "No company is associated with this recruiter."
        }), 400

    rows_deleted = delete_company_drive(
        company_id,
        drive_id
    )

    if rows_deleted == 0:
        return jsonify({
            "message": "Placement drive not found for your company."
        }), 404

    return jsonify({
        "message": "Placement drive deleted successfully"
    }), 200