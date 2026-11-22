
FROM python:3.11-slim-bookworm

ARG SPARK_VERSION=3.5.6
ARG ICEBERG_VERSION=1.9.2

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
    PYSPARK_PYTHON=python3 \
    PYSPARK_DRIVER_PYTHON=python3

# Install Java and system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
      openjdk-17-jre-headless \
      curl \
      tini \
      procps \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
      pyspark==${SPARK_VERSION} \
      jupyterlab==4.4.5 \
      ipykernel==6.30.1 \
      ipython-sql==0.5.0 \
      sqlalchemy==2.0.43 \
      pandas==2.3.1 \
      pyarrow==21.0.0 \
      matplotlib==3.10.5 \
      seaborn==0.13.2 \
      boto3==1.40.18 \
      s3fs==2025.7.0 \
      "pyiceberg[pyarrow,duckdb,pandas]"

# Configure SPARK_HOME from the actual PySpark installation
ENV SPARK_HOME=/usr/local/lib/python3.11/site-packages/pyspark
ENV PATH="${SPARK_HOME}/bin:${PATH}"
ENV PYTHONPATH="${SPARK_HOME}/python:${SPARK_HOME}/python/lib/py4j-0.10.9.9-src.zip"

# Verify Spark installation and create directories
RUN python -c "import pyspark; print('PySpark:', pyspark.__version__); print('Location:', pyspark.__file__)" \
    && test -f "${SPARK_HOME}/bin/spark-submit" \
    && mkdir -p \
        "${SPARK_HOME}/jars" \
        /workspace/notebooks \
        /workspace/data \
        /workspace/images

# Install Apache Iceberg Spark runtime and AWS bundle
RUN curl -fsSL \
    "https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/${ICEBERG_VERSION}/iceberg-spark-runtime-3.5_2.12-${ICEBERG_VERSION}.jar" \
    -o "${SPARK_HOME}/jars/iceberg-spark-runtime-3.5_2.12-${ICEBERG_VERSION}.jar" \
    && curl -fsSL \
    "https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-aws-bundle/${ICEBERG_VERSION}/iceberg-aws-bundle-${ICEBERG_VERSION}.jar" \
    -o "${SPARK_HOME}/jars/iceberg-aws-bundle-${ICEBERG_VERSION}.jar"

# Jupyter entrypoint
COPY docker/jupyter-entrypoint.sh /usr/local/bin/jupyter-entrypoint.sh

RUN chmod +x /usr/local/bin/jupyter-entrypoint.sh

WORKDIR /workspace

EXPOSE 8888 4040

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/jupyter-entrypoint.sh"]
