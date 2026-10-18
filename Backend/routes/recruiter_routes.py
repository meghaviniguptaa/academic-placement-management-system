from flask import Blueprint, jsonify, session, request

from auth.decorators import roles_required
from config.db import get_connection


recruiter_routes = Blueprint("recruiter_routes", __name__)


@recruiter_routes.route("/api/recruiter/company", methods=["GET"])
@roles_required("RECRUITER")
def get_recruiter_company():
    company_id = session.get("company_id")

    if not company_id:
        return jsonify({
            "message": "No company is associated with this recruiter."
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT Company_ID,
                   Company_Name,
                   Industry,
                   Contact_Email,
                   HR_Name,
                   Location
            FROM Companies
            WHERE Company_ID = :company_id
        """, {
            "company_id": company_id
        })

        row = cursor.fetchone()

        if not row:
            return jsonify({
                "message": "Company not found."
            }), 404

        columns = [col[0] for col in cursor.description]
        company = dict(zip(columns, row))

        return jsonify(company), 200

    except Exception:
        return jsonify({
            "message": "Unable to fetch company details."
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


@recruiter_routes.route("/api/recruiter/company", methods=["PUT"])
@roles_required("RECRUITER")
def update_recruiter_company():
    company_id = session.get("company_id")

    if not company_id:
        return jsonify({
            "message": "No company is associated with this recruiter."
        }), 400

    company = request.get_json()

    if not company:
        return jsonify({
            "message": "Request body is required."
        }), 400

    allowed_fields = [
        "Company_Name",
        "Industry",
        "Contact_Email",
        "HR_Name",
        "Location"
    ]

    updates = []
    params = {
        "company_id": company_id
    }

    for field in allowed_fields:
        if field in company:
            updates.append(f"{field} = :{field}")
            params[field] = company[field]

    if not updates:
        return jsonify({
            "message": "No valid company fields provided."
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            f"""
            UPDATE Companies
            SET {", ".join(updates)}
            WHERE Company_ID = :company_id
            """,
            params
        )

        if cursor.rowcount == 0:
            return jsonify({
                "message": "Company not found."
            }), 404

        connection.commit()

        return jsonify({
            "message": "Company updated successfully."
        }), 200

    except Exception:
        if connection is not None:
            connection.rollback()

        return jsonify({
            "message": "Unable to update company details."
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()