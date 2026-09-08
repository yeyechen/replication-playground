-- comp_events.sql
-- Purpose: Table 8 Compustat event months linked to CRSP permnos via CCM.
--   Panel A (pa): earnings-announcement months = calendar month of fundq.rdq
--                 (rdq non-null, <= 2002-12-31).
--   Panel D (pd): fiscal year-end months = calendar month of funda.datadate
--                 AND the following month (paper L2865).
-- Tables: comp_202601.fundq, comp_202601.funda, crsp_202601.ccmxpf_lnkhist
-- Output columns: panel ('pa'|'pd'), permno, event_month (Date32, month start)
-- Depends on: (none)
-- Settings: join_algorithm=partial_merge, max_execution_time=600
WITH
ea AS
(
    SELECT gvkey, toStartOfMonth(toDate32(rdq)) AS event_month
    FROM comp_202601.fundq
    WHERE indfmt = 'INDL' AND consol = 'C' AND popsrc = 'D'
      AND rdq IS NOT NULL
      AND toDate32(rdq) <= toDate32('2002-12-31')
    GROUP BY gvkey, event_month
),
fy AS
(
    SELECT gvkey, arrayJoin(
        [toStartOfMonth(toDate32(datadate)),
         addMonths(toStartOfMonth(toDate32(datadate)), 1)]) AS event_month
    FROM comp_202601.funda
    WHERE indfmt = 'INDL' AND consol = 'C' AND popsrc = 'D'
      AND datadate IS NOT NULL
      AND toDate32(datadate) <= toDate32('2002-11-30')  -- keep month+1 <= Dec02
    GROUP BY gvkey, event_month
),
lnk AS
(
    SELECT DISTINCT gvkey, lpermno AS permno,
           ifNull(toDate32(linkdt), toDate32('1900-01-01')) AS ldt,
           if(linkenddt IS NULL OR toDate32(linkenddt) < toDate32('1900-01-01'),
              toDate32('9999-12-31'), toDate32(linkenddt)) AS ledt
    FROM crsp_202601.ccmxpf_lnkhist
    WHERE linktype IN ('LC', 'LU', 'LS')      -- standard CCM filters
      AND linkprim IN ('P', 'C')
)
SELECT DISTINCT 'pa' AS panel, l.permno, e.event_month
FROM ea AS e
INNER JOIN lnk AS l ON e.gvkey = l.gvkey
WHERE addMonths(e.event_month, 1) > l.ldt    -- linkdt <= month end
  AND e.event_month <= l.ledt                -- linkenddt >= month start
UNION ALL
SELECT DISTINCT 'pd' AS panel, l.permno, f.event_month
FROM fy AS f
INNER JOIN lnk AS l ON f.gvkey = l.gvkey
WHERE addMonths(f.event_month, 1) > l.ldt
  AND f.event_month <= l.ledt
SETTINGS join_algorithm = 'partial_merge', max_execution_time = 600,
         max_rows_to_read = 10000000000
