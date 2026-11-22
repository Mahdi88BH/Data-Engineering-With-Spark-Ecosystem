-- Table "tampon" qui consomme le topic Kafka
CREATE TABLE IF NOT EXISTS purchases_kafka (
    value String
) ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'kafka:29092',
    kafka_topic_list = 'cdc.public.purchases',
    kafka_group_name = 'clickhouse_purchases_consumer',
    kafka_format = 'JSONAsString',
    kafka_num_consumers = 1;

-- Table cible (stockage durable)
CREATE TABLE IF NOT EXISTS purchases (
    id UInt64,
    user_id UInt64,
    item_id UInt64,
    campaign_id String,
    quantity UInt32,
    purchase_price Float64,
    created_at DateTime,
    _ingested_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (created_at, id);

-- Vue matérialisée : parse le JSON Debezium {before, after, op, ...}
CREATE MATERIALIZED VIEW IF NOT EXISTS purchases_mv TO purchases AS
SELECT
    JSONExtractUInt(value, 'after', 'id')                   AS id,
    JSONExtractUInt(value, 'after', 'user_id')              AS user_id,
    JSONExtractUInt(value, 'after', 'item_id')              AS item_id,
    JSONExtractString(value, 'after', 'campaign_id')        AS campaign_id,
    JSONExtractUInt(value, 'after', 'quantity')             AS quantity,
    JSONExtractFloat(value, 'after', 'purchase_price')      AS purchase_price,
    parseDateTimeBestEffort(
        JSONExtractString(value, 'after', 'created_at')
    )                                                       AS created_at
FROM purchases_kafka
WHERE JSONExtractString(value, 'op') IN ('c', 'u', 'r');