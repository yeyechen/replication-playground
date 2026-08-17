-- 01_universe_daily.sql
-- Build the universe-filtered daily panel (PIT shrcd/exchcd join)
-- Universe: shrcd IN (10, 11), exchcd IN (1, 2, 3), price >= $5
-- SIC exclusion: NOT (siccd BETWEEN 4900 AND 4949) AND NOT (siccd BETWEEN 6000 AND 6999)
-- Min 15 daily obs per stock-month
-- This produces a per-(permno, year_month) daily panel of valid stock-day observations

SELECT
    d.permno,
    toDate(d.date) AS date,
    toYYYYMM(d.date) AS month,
    d.ret,
    d.prc AS price,
    d.vol,
    d.shrout,
    d.hexcd,
    d.hsiccd,
    m.shrcd,
    m.exchcd,
    m.siccd
FROM crsp_202601.dsf d
INNER JOIN crsp_202601.dsenames m
    ON d.permno = m.permno
    AND toDate(d.date) >= toDate(m.namedt)
    AND (toDate(m.nameendt) = '1970-01-01' OR toDate(m.nameendt) >= toDate(d.date))
WHERE toDate(d.date) >= '1968-01-01'
  AND toDate(d.date) <= '2022-12-31'
  AND d.ret IS NOT NULL
  AND d.ret > -1.0  -- CRSP sentinel
  AND m.shrcd IN (10, 11)
  AND m.exchcd IN (1, 2, 3)
  AND abs(d.prc) >= 5.0
  AND NOT (m.siccd BETWEEN 4900 AND 4949)
  AND NOT (m.siccd BETWEEN 6000 AND 6999)
SETTINGS max_execution_time = 600,
         max_rows_to_read = 5000000000,
         timeout_before_checking_execution_speed = 0
