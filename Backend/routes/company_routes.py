from flask import Blueprint, jsonify, request

from auth.decorators import roles_required
from controllers.company_controller import (
    get_all_companies,
    create_company,
    update_company,
    delete_company
)


company_routes = Blueprint("company_routes", __name__)


# GET - Read all companies
@company_routes.route("/api/companies", methods=["GET"])
@roles_required("ADMIN")
def get_companies():
    companies = get_all_companies()
    return jsonify(companies)


# POST - Create a company
@company_routes.route("/api/companies", methods=["POST"])
@roles_required("ADMIN")
def add_company():
    company = request.get_json()

    create_company(company)

    return jsonify({
        "message": "Company created successfully"
    }), 201


# PUT - Update a company
@company_routes.route("/api/companies/<int:company_id>", methods=["PUT"])
@roles_required("ADMIN")
def edit_company(company_id):
    company = request.get_json()

    rows_updated = update_company(company_id, company)

    if rows_updated == 0:
        return jsonify({
            "message": "Company not found"
        }), 404

    return jsonify({
        "message": "Company updated successfully"
    })


# DELETE - Delete a company
@company_routes.route("/api/companies/<int:company_id>", methods=["DELETE"])
@roles_required("ADMIN")
def remove_company(company_id):
    rows_deleted = delete_company(company_id)

    if rows_deleted == 0:
        return jsonify({
            "message": "Company not found"
        }), 404

    return jsonify({
        "message": "Company deleted successfully"
    })