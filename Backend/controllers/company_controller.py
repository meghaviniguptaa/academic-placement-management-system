from config.db import get_connection


def get_all_companies():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT Company_ID, Company_Name, Industry,
               Contact_Email, HR_Name, Location
        FROM Companies
    """)

    columns = [col[0] for col in cursor.description]
    companies = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return companies


def create_company(company):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO Companies
        (Company_ID, Company_Name, Industry,
         Contact_Email, HR_Name, Location)
        VALUES
        (:1, :2, :3, :4, :5, :6)
    """, (
        company["Company_ID"],
        company["Company_Name"],
        company["Industry"],
        company["Contact_Email"],
        company["HR_Name"],
        company["Location"]
    ))

    connection.commit()

    cursor.close()
    connection.close()


def update_company(company_id, company):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE Companies
        SET Company_Name = :1,
            Industry = :2,
            Contact_Email = :3,
            HR_Name = :4,
            Location = :5
        WHERE Company_ID = :6
    """, (
        company["Company_Name"],
        company["Industry"],
        company["Contact_Email"],
        company["HR_Name"],
        company["Location"],
        company_id
    ))

    rows_updated = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    return rows_updated


def delete_company(company_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM Companies
        WHERE Company_ID = :1
    """, (company_id,))

    rows_deleted = cursor.rowcount

    connection.commit()

    cursor.close()
    connection.close()

    return rows_deleted