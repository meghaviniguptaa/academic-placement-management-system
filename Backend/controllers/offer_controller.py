from config.db import get_connection


def get_all_offers():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT Offer_ID, Application_ID, Offer_Date,
               Offered_Package_LPA, Offer_Status
        FROM Offers
    """)

    columns = [col[0] for col in cursor.description]
    offers = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return offers


def create_offer(offer):
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

    cursor.close()
    connection.close()


def update_offer(offer_id, offer):
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

    cursor.close()
    connection.close()

    return rows_updated


def delete_offer(offer_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM Offers
        WHERE Offer_ID = :1
    """, (offer_id,))

    rows_deleted = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    return rows_deleted