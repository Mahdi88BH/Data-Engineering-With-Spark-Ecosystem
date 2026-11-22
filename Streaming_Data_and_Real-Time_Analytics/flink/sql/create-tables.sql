-- =========================================================================
--  Source : raw login events
-- =========================================================================
CREATE TABLE login_events (
  user_id     STRING,
  `timestamp` STRING,
  ip          STRING,
  device      STRING,
  platform    STRING,
  user_agent  STRING,
  -- colonne calculée : ISO string → TIMESTAMP (nécessaire pour les fenêtres)
  event_ts AS TO_TIMESTAMP(REPLACE(REPLACE(`timestamp`, 'T', ' '), 'Z', '')),
  WATERMARK FOR event_ts AS event_ts - INTERVAL '5' SECOND
) WITH (
  'connector'                     = 'kafka',
  'topic'                         = 'login-events',
  'properties.bootstrap.servers'  = 'kafka:29092',
  'properties.group.id'           = 'flink-login-events-v1',
  'format'                        = 'json',
  'json.fail-on-missing-field'    = 'false',
  'json.ignore-parse-errors'      = 'true',
  'scan.startup.mode'             = 'earliest-offset'
);


-- =========================================================================
--  Sink : événements enrichis
-- =========================================================================
CREATE TABLE login_events_enriched (
  user_id     STRING,
  `timestamp` STRING,
  ip          STRING,
  platform    STRING,
  device_type STRING,
  country     STRING,
  city        STRING,
  PRIMARY KEY (user_id, `timestamp`) NOT ENFORCED
) WITH (
  'connector'                     = 'upsert-kafka',
  'topic'                         = 'login-events-enriched',
  'properties.bootstrap.servers'  = 'kafka:29092',
  'key.format'                    = 'json',
  'value.format'                  = 'json'
);

-- =========================================================================
--  Source : relecture du topic enrichi (pour la détection d'anomalies)
--  -- Consumer group DIFFÉRENT de celui de l'écriture --
-- =========================================================================
CREATE TABLE login_events_enriched_src (
  user_id     STRING,
  `timestamp` STRING,
  ip          STRING,
  platform    STRING,
  device_type STRING,
  country     STRING,
  city        STRING,
  event_ts AS TO_TIMESTAMP(REPLACE(REPLACE(`timestamp`, 'T', ' '), 'Z', '')),
  WATERMARK FOR event_ts AS event_ts - INTERVAL '5' SECOND
) WITH (
  'connector'                     = 'kafka',
  'topic'                         = 'login-events-enriched',
  'properties.bootstrap.servers'  = 'kafka:29092',
  'properties.group.id'           = 'flink-enriched-reader-v1',
  'format'                        = 'json',
  'json.fail-on-missing-field'    = 'false',
  'json.ignore-parse-errors'      = 'true',
  'scan.startup.mode'             = 'earliest-offset'
);

-- =========================================================================
--  Sink : anomalies
-- =========================================================================
CREATE TABLE login_anomalies (
  user_id     STRING,
  `timestamp` STRING,
  reason      STRING,
  country     STRING,
  PRIMARY KEY (user_id, `timestamp`) NOT ENFORCED
) WITH (
  'connector'                     = 'upsert-kafka',
  'topic'                         = 'login-anomalies',
  'properties.bootstrap.servers'  = 'kafka:29092',
  'key.format'                    = 'json',
  'value.format'                  = 'json'
);