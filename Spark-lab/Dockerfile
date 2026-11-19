FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV SPARK_VERSION=3.5.1
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=${SPARK_HOME}/bin:${PATH}
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    bash \
    tini \
    openjdk-17-jdk \
    procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --timeout=120 --retries=5 \
    pyspark==3.5.1 \
 && pip install --no-cache-dir --timeout=120 --retries=5 \
    jupyterlab \
    pandas \
    numpy \
    matplotlib

# Spark est fourni par le paquet pyspark : on le rend accessible via /opt/spark
RUN ln -s /usr/local/lib/python3.11/site-packages/pyspark /opt/spark

WORKDIR /opt/spark-notebooks

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["bash"]