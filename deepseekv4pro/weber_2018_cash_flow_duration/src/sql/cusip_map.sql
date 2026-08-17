-- cusip_map.sql
-- Purpose: Point-in-time 8-digit CUSIP -> permno mapping from CRSP names history.
--          Used to map TR-13F 8-char CUSIPs (s34.cusip) to CRSP permnos at each
--          report quarter. Prefer ncusip (normalised, carried forward across
--          historical CUSIP changes) but also keep raw cusip for fallback.
-- Tables: crsp_202601.dsenames
-- Output columns: cusip (String), permno (Int32), namedt (Date32), nameendt (Date32)
-- Depends on: none
-- Settings: max_execution_time=300
--
-- dsenames namedt/nameendt give the validity window of a name (and CUSIP) record.
-- nameendt is the LAST day the record is valid (inclusive). We emit both the
-- normalised and raw CUSIP so Python can try ncusip first, then cusip.

SELECT
    ncusip AS cusip,
    permno,
    toDate32(namedt) AS namedt,
    toDate32(nameendt) AS nameendt
FROM crsp_202601.dsenames
WHERE ncusip IS NOT NULL AND ncusip != ''
UNION ALL
SELECT
    cusip AS cusip,
    permno,
    toDate32(namedt) AS namedt,
    toDate32(nameendt) AS nameendt
FROM crsp_202601.dsenames
WHERE cusip IS NOT NULL AND cusip != ''
SETTINGS max_execution_time = 300,
         max_rows_to_read = 2000000,
         timeout_before_checking_execution_speed = 0
