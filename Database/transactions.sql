
SET SERVEROUTPUT ON
SET AUTOCOMMIT OFF

-- =====================================================
-- ACADEMIC PLACEMENT MANAGEMENT SYSTEM
-- TRANSACTION MANAGEMENT DEMONSTRATION
-- Application ID: 508
-- =====================================================

-- Store the original status for restoration
VARIABLE original_status VARCHAR2(20);

BEGIN
    SELECT Status
    INTO :original_status
    FROM Applications
    WHERE Application_ID = 508;
END;
/

PRINT original_status


-- =====================================================
-- 1. COMMIT
-- Save a change permanently, then restore the original
-- status in a separate committed transaction.
-- =====================================================

UPDATE Applications
SET Status = 'SHORTLISTED'
WHERE Application_ID = 508;

COMMIT;

SELECT Application_ID, Status
FROM Applications
WHERE Application_ID = 508;

-- Restore the original status
UPDATE Applications
SET Status = :original_status
WHERE Application_ID = 508;

COMMIT;


-- =====================================================
-- 2. ROLLBACK
-- Undo an uncommitted change.
-- =====================================================

UPDATE Applications
SET Status = 'WITHDRAWN'
WHERE Application_ID = 508;

ROLLBACK;

SELECT Application_ID, Status
FROM Applications
WHERE Application_ID = 508;


-- =====================================================
-- 3. SAVEPOINT
-- Undo only the changes made after the savepoint.
-- =====================================================

UPDATE Applications
SET Status = 'SHORTLISTED'
WHERE Application_ID = 508;

SAVEPOINT first_update;

UPDATE Applications
SET Status = 'WITHDRAWN'
WHERE Application_ID = 508;

ROLLBACK TO first_update;

SELECT Application_ID, Status
FROM Applications
WHERE Application_ID = 508;

-- Undo the remaining uncommitted change
ROLLBACK;

SELECT Application_ID, Status
FROM Applications
WHERE Application_ID = 508;

PROMPT Transaction demonstrations completed.
