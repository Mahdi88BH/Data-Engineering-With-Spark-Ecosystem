SET 'execution.attached' = 'false';

-- =========================================================================
--  JOB 1 : Enrichissement (geo + device_type) via CASE (sans fichier)
-- =========================================================================
INSERT INTO login_events_enriched
SELECT
  e.user_id,
  e.`timestamp`,
  e.ip,
  e.platform,
  CASE
    WHEN LOWER(e.device) LIKE '%iphone%'
      OR LOWER(e.device) LIKE '%samsung%'
      OR LOWER(e.device) LIKE '%pixel%'
      OR LOWER(e.device) LIKE '%android%' THEN 'mobile'
    ELSE 'desktop'
  END                                          AS device_type,
  CASE
    WHEN e.ip LIKE '192.168.%'    THEN 'United States'
    WHEN e.ip LIKE '203.0.113.%'  THEN 'Germany'
    WHEN e.ip LIKE '10.0.%'       THEN 'France'
    ELSE 'Unknown'
  END                                          AS country,
  CASE
    WHEN e.ip LIKE '192.168.%'    THEN 'New York'
    WHEN e.ip LIKE '203.0.113.%'  THEN 'Berlin'
    WHEN e.ip LIKE '10.0.%'       THEN 'Paris'
    ELSE 'Unknown'
  END                                          AS city
FROM login_events e;

-- =========================================================================
--  JOB 2 : Détection d'anomalie (inchangé)
-- =========================================================================
INSERT INTO login_anomalies
SELECT
  user_id,
  CAST(window_end AS STRING)                              AS `timestamp`,
  'Multiple countries within 2 minutes'                   AS reason,
  CAST(COUNT(DISTINCT country) AS STRING) || ' countries' AS country
FROM TABLE(
  TUMBLE(
    TABLE login_events_enriched_src,
    DESCRIPTOR(event_ts),
    INTERVAL '2' MINUTES
  )
)
GROUP BY user_id, window_start, window_end
HAVING COUNT(DISTINCT country) >= 2;