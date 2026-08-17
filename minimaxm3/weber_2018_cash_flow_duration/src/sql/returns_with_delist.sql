-- returns_with_delist.sql
-- Purpose: Monthly returns with Shumway (1997) delisting treatment.
--
-- Treatment (paper §2 L104):
--   - For a security with performance-related delisting (dlstcd in 400-591) AND
--     missing dlret (dlret is NULL or one of {-44,-55,-66,-77,-88,-99}), substitute
--     -0.30 (-30%).
--   - dlret is then added to the last monthly ret (or pro-rated if the delisting
--     return spans multiple months after the security stopped trading — Cohen et al.
--     2009 treatment; we approximate by adding dlret to the delisting-month ret when
--     dlret is in (-1, +1]).
--
-- The Shumway substitution is implemented in Python (main.py) after the SQL
-- join. This SQL pulls the inputs needed:
--   - permno, date, ret, retx, prc, shrout, hexcd
--   - delisting code (from dsedelist.dlstcd) and delisting return (from dsedelist.dlret)
--     joined PIT to the month when the security stopped trading.
--
-- Tables:  crsp_202601.msf, crsp_202601.dsedelist
-- Output columns: permno, month_date, ret, retx, prc, shrout, hexcd, dlstcd, dlret
-- Depends on: (none)

WITH
  msf_dates AS (
    SELECT
      permno,
      toDate32(date)             AS month_date,
      ret,
      retx,
      prc,
      shrout,
      hexcd
    FROM crsp_202601.msf
    WHERE permno IS NOT NULL
      AND date >= '1963-01-01'
      AND date <= '2014-12-31'
  ),
  delist AS (
    SELECT
      permno,
      toDate32OrNull(dlstdt) AS dlstdt,
      dlstcd,
      -- Treat missing-return sentinels as NULL
      if(dlret < -0.40 OR dlret IS NULL, NULL, dlret) AS dlret
    FROM crsp_202601.dsedelist
    WHERE permno IS NOT NULL
  )
SELECT
  m.permno        AS permno,
  m.month_date    AS month_date,
  m.ret           AS ret,
  m.retx          AS retx,
  m.prc           AS prc,
  m.shrout        AS shrout,
  m.hexcd         AS hexcd,
  d.dlstcd        AS dlstcd,
  d.dlstdt        AS dlstdt,
  d.dlret         AS dlret
FROM msf_dates AS m
LEFT ANY JOIN delist AS d
  ON m.permno = d.permno
 -- Only attach the delisting code to the delisting month (and the month after
 -- if the delisting return is reported with a lag). For Shumway treatment,
 -- we only need dlstcd/dlret for the delisting month itself.
 AND m.month_date = d.dlstdt
