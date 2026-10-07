from flask import Blueprint, jsonify, request

from controllers.offer_controller import (
    get_all_offers,
    create_offer,
    update_offer,
    delete_offer
)

offer_routes = Blueprint("offer_routes", __name__)


@offer_routes.route("/api/offers", methods=["GET"])
def get_offers():
    offers = get_all_offers()
    return jsonify(offers)


@offer_routes.route("/api/offers", methods=["POST"])
def add_offer():
    offer = request.get_json()
    create_offer(offer)

    return jsonify({
        "message": "Offer created successfully"
    }), 201


@offer_routes.route("/api/offers/<int:offer_id>", methods=["PUT"])
def edit_offer(offer_id):
    offer = request.get_json()
    rows_updated = update_offer(offer_id, offer)

    if rows_updated == 0:
        return jsonify({
            "message": "Offer not found"
        }), 404

    return jsonify({
        "message": "Offer updated successfully"
    })


@offer_routes.route("/api/offers/<int:offer_id>", methods=["DELETE"])
def remove_offer(offer_id):
    rows_deleted = delete_offer(offer_id)

    if rows_deleted == 0:
        return jsonify({
            "message": "Offer not found"
        }), 404

    return jsonify({
        "message": "Offer deleted successfully"
    })