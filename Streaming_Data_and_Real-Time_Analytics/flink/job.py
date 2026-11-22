'''
import json
from pyflink.common import WatermarkStrategy, Types
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import (
    KafkaSource, KafkaSink, KafkaRecordSerializationSchema, KafkaOffsetsInitializer
)
from pyflink.datastream.functions import MapFunction, KeyedProcessFunction
from pyflink.datastream.state import ValueStateDescriptor

KAFKA = "kafka:29092"

# ---------- Enrichissement IP → pays, device → type ----------
IP_COUNTRY = {
    "192.168.1.100": "United States",
    "203.0.113.22":  "Germany",
    "10.0.0.99":     "France",
}

def device_type(device: str) -> str:
    if "iPhone" in device or "Samsung" in device:
        return "mobile"
    return "desktop"


class EnrichFunction(MapFunction):
    def map(self, raw):
        evt = json.loads(raw)
        evt["country"]     = IP_COUNTRY.get(evt.get("ip"), "Unknown")
        evt["device_type"] = device_type(evt.get("device", ""))
        return json.dumps(evt)


# ---------- Détection d'anomalie : changement d'IP par utilisateur ----------
class AnomalyDetector(KeyedProcessFunction):
    def open(self, ctx):
        self._last_ip = ctx.get_state(
            ValueStateDescriptor("last_ip", Types.STRING())
        )

    def process_element(self, value, ctx):
        evt = json.loads(value)
        prev_ip = self._last_ip.value()
        curr_ip = evt.get("ip")

        if prev_ip is not None and prev_ip != curr_ip:
            anomaly = dict(evt)
            anomaly["anomaly_type"] = "ip_change"
            anomaly["previous_ip"]  = prev_ip
            yield json.dumps(anomaly)

        self._last_ip.update(curr_ip)


# ---------- Job ----------
env = StreamExecutionEnvironment.get_execution_environment()
env.enable_checkpointing(10_000)  # checkpoint toutes les 10s
env.set_parallelism(2)            # 2 parallèles (sur 20 slots dispo)

# Source
source = (
    KafkaSource.builder()
    .set_bootstrap_servers(KAFKA)
    .set_topics("login-events")
    .set_group_id("flink-login-enricher")
    .set_starting_offsets(KafkaOffsetsInitializer.earliest())
    .set_value_only_deserializer(SimpleStringSchema())
    .build()
)

# Sink enriched
sink_enriched = (
    KafkaSink.builder()
    .set_bootstrap_servers(KAFKA)
    .set_record_serializer(
        KafkaRecordSerializationSchema.builder()
        .set_topic("login-events-enriched")
        .set_value_serialization_schema(SimpleStringSchema())
        .build()
    )
    .build()
)

# Sink anomalies
sink_anomalies = (
    KafkaSink.builder()
    .set_bootstrap_servers(KAFKA)
    .set_record_serializer(
        KafkaRecordSerializationSchema.builder()
        .set_topic("login-anomalies")
        .set_value_serialization_schema(SimpleStringSchema())
        .build()
    )
    .build()
)

stream = env.from_source(
    source,
    WatermarkStrategy.no_watermarks(),
    "login-events-source",
)

# Enrichir
enriched = stream.map(EnrichFunction()).name("enrich")

# → topic enriched
enriched.sink_to(sink_enriched).name("sink-enriched")

# → détection anomalies → topic anomalies
(
    enriched
    .key_by(lambda s: json.loads(s)["user_id"], key_type=Types.STRING())
    .process(AnomalyDetector())
    .name("anomaly-detector")
    .sink_to(sink_anomalies)
    .name("sink-anomalies")
)

env.execute("login-enricher")
'''