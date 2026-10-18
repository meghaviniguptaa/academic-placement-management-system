
from flask import Blueprint, jsonify, request, current_app, session

from auth.decorators import roles_required
from utils.validation import is_positive_int

from controllers.offer_controller import (
    get_all_offers,
    create_offer,
    update_offer,
    delete_offer,
    get_my_offers,
    get_company_offers,
    create_company_offer,
    update_company_offer,
    delete_company_offer
)

offer_routes = Blueprint("offer_routes", __name__)

@offer_routes.route("/api/offers", methods=["GET"])
@roles_required("ADMIN")
def get_offers():
    try:
        offers = get_all_offers()
        return jsonify(offers), 200

    except Exception:
        current_app.logger.exception("Fetching offers failed")
        return jsonify({
            "message": "Unable to fetch offers."
        }), 500


@offer_routes.route("/api/offers", methods=["POST"])
@roles_required("ADMIN")
def add_offer():
    offer = request.get_json(silent=True)

    if not isinstance(offer, dict):
        return jsonify({
            "message": "A JSON request body is required."
        }), 400

    try:
        create_offer(offer)

        return jsonify({
            "message": "Offer created successfully."
        }), 201

    except Exception:
        current_app.logger.exception("Creating offer failed")
        return jsonify({
            "message": "Unable to create offer."
        }), 500


@offer_routes.route("/api/offers/<int:offer_id>", methods=["PUT"])
@roles_required("ADMIN")
def edit_offer(offer_id):
    offer = request.get_json(silent=True)

    if not isinstance(offer, dict):
        return jsonify({
            "message": "A JSON request body is required."
        }), 400

    try:
        rows_updated = update_offer(offer_id, offer)

        if rows_updated == 0:
            return jsonify({
                "message": "Offer not found."
            }), 404

        return jsonify({
            "message": "Offer updated successfully."
        }), 200

    except Exception:
        current_app.logger.exception("Updating offer failed")
        return jsonify({
            "message": "Unable to update offer."
        }), 500


@offer_routes.route("/api/offers/<int:offer_id>", methods=["DELETE"])
@roles_required("ADMIN")
def remove_offer(offer_id):
    try:
        rows_deleted = delete_offer(offer_id)

        if rows_deleted == 0:
            return jsonify({
                "message": "Offer not found."
            }), 404

        return jsonify({
            "message": "Offer deleted successfully."
        }), 200

    except Exception:
        current_app.logger.exception("Deleting offer failed")
        return jsonify({
            "message": "Unable to delete offer."
        }), 500


# --------------------------------------------------
# GET - View offers for the logged-in student
# --------------------------------------------------
@offer_routes.route("/api/student/offers", methods=["GET"])
@roles_required("STUDENT")
def get_student_offers():
    student_id = session.get("student_id")

    if not is_positive_int(student_id):
        return jsonify({
            "message": "Student account is not linked to a profile."
        }), 403

    try:
        offers = get_my_offers(student_id)
        return jsonify(offers), 200

    except Exception:
        current_app.logger.exception(
            "Fetching student offers failed"
        )
        return jsonify({
            "message": "Unable to fetch offers."
        }), 500

@offer_routes.route("/api/recruiter/offers", methods=["GET"])
@roles_required("RECRUITER")
def get_recruiter_offers():
    company_id = session.get("company_id")

    if not is_positive_int(company_id):
        return jsonify({"message": "Recruiter account is not linked to a company."}), 403

    try:
        offers = get_company_offers(company_id)
        return jsonify(offers), 200
    except Exception:
        current_app.logger.exception("Fetching recruiter offers failed")
        return jsonify({"message": "Unable to fetch offers."}), 500


@offer_routes.route("/api/recruiter/offers", methods=["POST"])
@roles_required("RECRUITER")
def add_recruiter_offer():
    company_id = session.get("company_id")

    if not is_positive_int(company_id):
        return jsonify({"message": "Recruiter account is not linked to a company."}), 403

    offer = request.get_json(silent=True)

    if not isinstance(offer, dict):
        return jsonify({"message": "A JSON request body is required."}), 400

    required_fields = [
        "Offer_ID",
        "Application_ID",
        "Offer_Date",
        "Offered_Package_LPA",
        "Offer_Status"
    ]

    if any(field not in offer for field in required_fields):
        return jsonify({"message": "Missing required offer fields."}), 400

    try:
        create_company_offer(company_id, offer)
        return jsonify({"message": "Offer created successfully."}), 201
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 400
    except Exception:
        current_app.logger.exception("Creating recruiter offer failed")
        return jsonify({"message": "Unable to create offer."}), 500


@offer_routes.route("/api/recruiter/offers/<int:offer_id>", methods=["PUT"])
@roles_required("RECRUITER")
def edit_recruiter_offer(offer_id):
    company_id = session.get("company_id")

    if not is_positive_int(company_id):
        return jsonify({"message": "Recruiter account is not linked to a company."}), 403

    offer = request.get_json(silent=True)

    if not isinstance(offer, dict):
        return jsonify({"message": "A JSON request body is required."}), 400

    required_fields = [
        "Offer_Date",
        "Offered_Package_LPA",
        "Offer_Status"
    ]

    if any(field not in offer for field in required_fields):
        return jsonify({"message": "Missing required offer fields."}), 400

    try:
        rows_updated = update_company_offer(
            company_id,
            offer_id,
            offer
        )

        if rows_updated == 0:
            return jsonify({"message": "Offer not found."}), 404

        return jsonify({"message": "Offer updated successfully."}), 200

    except Exception:
        current_app.logger.exception("Updating recruiter offer failed")
        return jsonify({"message": "Unable to update offer."}), 500


@offer_routes.route("/api/recruiter/offers/<int:offer_id>", methods=["DELETE"])
@roles_required("RECRUITER")
def remove_recruiter_offer(offer_id):
    company_id = session.get("company_id")

    if not is_positive_int(company_id):
        return jsonify({"message": "Recruiter account is not linked to a company."}), 403

    try:
        rows_deleted = delete_company_offer(
            company_id,
            offer_id
        )

        if rows_deleted == 0:
            return jsonify({"message": "Offer not found."}), 404

        return jsonify({"message": "Offer deleted successfully."}), 200

    except Exception:
        current_app.logger.exception("Deleting recruiter offer failed")
        return jsonify({"message": "Unable to delete offer."}), 500