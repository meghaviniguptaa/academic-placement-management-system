SET SQLBLANKLINES ON

/* =========================================================
   ACADEMIC PLACEMENT MANAGEMENT SYSTEM
   STORED PROCEDURES
   ========================================================= */


/* =========================================================
   1. UPDATE APPLICATION STATUS
   Purpose:
   Updates the status of an application after validating
   that the application exists and the new status is valid.
   ========================================================= */

CREATE OR REPLACE PROCEDURE Update_Application_Status (
    p_application_id IN Applications.Application_ID%TYPE,
    p_new_status     IN Applications.Status%TYPE
)
AS
    v_count NUMBER;
BEGIN

    /* Check whether the application exists */
    SELECT COUNT(*)
    INTO v_count
    FROM Applications
    WHERE Application_ID = p_application_id;

    IF v_count = 0 THEN
        RAISE_APPLICATION_ERROR(
            -20001,
            'Application ID does not exist.'
        );
    END IF;


    /* Validate the new application status */
    IF p_new_status NOT IN
       ('APPLIED', 'SHORTLISTED', 'REJECTED', 'SELECTED', 'WITHDRAWN')
    THEN
        RAISE_APPLICATION_ERROR(
            -20002,
            'Invalid application status.'
        );
    END IF;


    /* Update the application */
    UPDATE Applications
    SET Status = p_new_status
    WHERE Application_ID = p_application_id;


    COMMIT;

END Update_Application_Status;
/


/* =========================================================
   2. UPDATE OFFER STATUS
   Purpose:
   Updates the status of an offer after validating
   that the offer exists and the new status is valid.
   ========================================================= */

CREATE OR REPLACE PROCEDURE Update_Offer_Status (
    p_offer_id     IN Offers.Offer_ID%TYPE,
    p_new_status   IN Offers.Offer_Status%TYPE
)
AS
    v_count NUMBER;
BEGIN

    /* Check whether the offer exists */
    SELECT COUNT(*)
    INTO v_count
    FROM Offers
    WHERE Offer_ID = p_offer_id;

    IF v_count = 0 THEN
        RAISE_APPLICATION_ERROR(
            -20003,
            'Offer ID does not exist.'
        );
    END IF;


    /* Validate the new offer status */
    IF p_new_status NOT IN
       ('PENDING', 'ACCEPTED', 'REJECTED')
    THEN
        RAISE_APPLICATION_ERROR(
            -20004,
            'Invalid offer status.'
        );
    END IF;


    /* Update the offer */
    UPDATE Offers
    SET Offer_Status = p_new_status
    WHERE Offer_ID = p_offer_id;


    COMMIT;

END Update_Offer_Status;
/