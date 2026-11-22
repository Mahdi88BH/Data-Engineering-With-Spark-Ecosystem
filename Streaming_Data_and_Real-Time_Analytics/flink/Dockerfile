FROM flink:1.19.1-scala_2.12-java17

# JAR Kafka connector (SQL)
RUN wget -q -P /opt/flink/lib/ \
    https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.2.0-1.19/flink-sql-connector-kafka-3.2.0-1.19.jar

USER root
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copier les scripts SQL et le fichier geo
WORKDIR /opt/flink
COPY sql/  /opt/flink/sql/
COPY ip_geo.csv /opt/flink/ip_geo.csv
COPY sql/sql-client-defaults.yaml /opt/flink/conf/sql-client-defaults.yaml

USER flink