from flask import Blueprint, jsonify, request
from auth.decorators import roles_required

from controllers.drive_controller import (
    get_all_drives,
    create_drive,
    update_drive,
    delete_drive
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