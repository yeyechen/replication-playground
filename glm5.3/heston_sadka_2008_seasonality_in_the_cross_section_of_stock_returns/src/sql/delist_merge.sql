-- delist_merge.sql
-- Purpose: Assumption 4 (REVISED). Delisting events for the panel merge:
--          permno, delisting calendar month, dlret, dlstcd (plus the
--          delisting-record hexcd/hsiccd for inserted rows). In main.py the
--          delisting-month return becomes (1+msf.ret)*(1+dlret)-1 when an
--          msf row exists, dlret alone when it does not (row inserted), and
--          -0.30 when dlret is missing and dlstcd is 500-599
--          (performance-related; all sample firms NYSE/AMEX).
-- Tables: crsp_202601.msedelist
-- Output columns: permno, dmonth, dlret, dlstcd, dl_hexcd, dl_hsiccd
-- Depends on: (none); merged onto universe_monthly.sql output in main.py
-- Notes: dlstdt is Nullable(String) -> parse with toDate32OrNull
--        (pre-1970 safety). The PIT shrcd/exchcd filter is applied in
--        Python via utils.apply_universe_filter on dmonth, the same
--        dsfhdr validity-window filter the msf rows get.
SELECT
    permno,
    toStartOfMonth(toDate32OrNull(dlstdt)) AS dmonth,
    dlret,
    dlstcd,
    hexcd AS dl_hexcd,
    hsiccd AS dl_hsiccd
FROM crsp_202601.msedelist
WHERE dlstdt IS NOT NULL
  AND dlstdt >= '1945-01-01'
  AND dlstdt <= '2002-12-31'
  AND permno IS NOT NULL
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;
