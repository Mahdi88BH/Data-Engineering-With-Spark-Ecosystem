FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 \
    PATH="/usr/lib/jvm/java-21-openjdk-amd64/bin:${PATH}" \
    SPARK_LOCAL_IP=127.0.0.1 \
    PYSPARK_PYTHON=python3 \
    PYSPARK_DRIVER_PYTHON=python3

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-21-jre-headless procps tini \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /workspace/notebooks /workspace/data /workspace/logs \
    && useradd --create-home --uid 1000 notebook \
    && chown -R notebook:notebook /workspace

USER notebook

EXPOSE 8888

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["sh", "-c", "jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --ServerApp.token=${JUPYTER_TOKEN:-deltalake} --ServerApp.root_dir=/workspace"]
