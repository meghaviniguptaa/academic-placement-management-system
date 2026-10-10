
from config.db import get_connection


# --------------------------------------------------
# GET ALL OFFERS (existing CRUD)
# --------------------------------------------------
def get_all_offers():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT Offer_ID, Application_ID, Offer_Date,
                   Offered_Package_LPA, Offer_Status
            FROM Offers
            ORDER BY Offer_Date DESC, Offer_ID DESC
        """)

        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


# --------------------------------------------------
# CREATE OFFER (existing CRUD)
# --------------------------------------------------
def create_offer(offer):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO Offers
                (Offer_ID, Application_ID, Offer_Date,
                 Offered_Package_LPA, Offer_Status)
            VALUES
                (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'), :4, :5)
        """, (
            offer["Offer_ID"],
            offer["Application_ID"],
            offer["Offer_Date"],
            offer["Offered_Package_LPA"],
            offer["Offer_Status"]
        ))

        connection.commit()

    except Exception:
        if connection is not None:
            connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


# --------------------------------------------------
# UPDATE OFFER (existing CRUD)
# --------------------------------------------------
def update_offer(offer_id, offer):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE Offers
            SET Application_ID = :1,
                Offer_Date = TO_DATE(:2, 'YYYY-MM-DD'),
                Offered_Package_LPA = :3,
                Offer_Status = :4
            WHERE Offer_ID = :5
        """, (
            offer["Application_ID"],
            offer["Offer_Date"],
            offer["Offered_Package_LPA"],
            offer["Offer_Status"],
            offer_id
        ))

        rows_updated = cursor.rowcount
        connection.commit()

        return rows_updated

    except Exception:
        if connection is not None:
            connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


# --------------------------------------------------
# DELETE OFFER (existing CRUD)
# --------------------------------------------------
def delete_offer(offer_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM Offers
            WHERE Offer_ID = :1
        """, (offer_id,))

        rows_deleted = cursor.rowcount
        connection.commit()

        return rows_deleted

    except Exception:
        if connection is not None:
            connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


# --------------------------------------------------
# GET OFFERS FOR THE LOGGED-IN STUDENT
# --------------------------------------------------
def get_my_offers(student_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                o.Offer_ID,
                o.Application_ID,
                j.Job_ID,
                j.Job_Title,
                c.Company_Name,
                o.Offer_Date,
                o.Offered_Package_LPA,
                o.Offer_Status
            FROM Offers o
            JOIN Applications a
                ON o.Application_ID = a.Application_ID
            JOIN Job_Postings j
                ON a.Job_ID = j.Job_ID
            JOIN Placement_Drives d
                ON j.Drive_ID = d.Drive_ID
            JOIN Companies c
                ON d.Company_ID = c.Company_ID
            WHERE a.Student_ID = :1
            ORDER BY o.Offer_Date DESC, o.Offer_ID DESC
        """, (student_id,))

        columns = [col[0] for col in cursor.description]

        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
