# PySpark + Apache Iceberg REST + SeaweedFS lab

A local Docker Compose learning environment for Spark SQL / PySpark, Apache Iceberg REST Catalog, and S3-compatible object storage provided by SeaweedFS.

## Architecture

- **JupyterLab**: notebooks, PySpark and `%%sql` support.
- **Apache Spark**: runs in local mode inside the Jupyter container.
- **Apache Iceberg REST Catalog**: catalog service on port 8181.
- **SeaweedFS**: master UI/API on 9333, volume UI on 8080, filer UI on 8889, S3 API on 8333.
- **S3 bucket**: `warehouse`, created automatically by the init service.

> This is a single-node learning lab, not a production deployment. Credentials are demo credentials. Do not expose these ports to an untrusted network.

## Compatibility choice

This starter intentionally uses **Spark 3.5.x + Scala 2.12 + Iceberg 1.9.2 runtime for Spark 3.5**. It avoids mixing Spark 4 with a runtime built for Spark 3.5. The PySpark version is pinned in the Dockerfile. The REST catalog is Apache's REST fixture backed by a SQLite JDBC catalog persisted in a Docker volume. SeaweedFS provides the S3-compatible endpoint.

## Start (Windows PowerShell)

1. Install Docker Desktop and ensure its Linux engine is running.
2. Copy the environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

3. Build and start:

   ```powershell
   docker compose up -d --build
   ```

4. Follow startup logs:

   ```powershell
   docker compose logs -f jupyter iceberg-rest seaweedfs seaweedfs-init
   ```

5. Open the UIs:

   | Service | URL | Purpose |
   |---|---|---|
   | JupyterLab | http://localhost:8888 | Notebooks and SQL magic |
   | Iceberg REST | http://localhost:8181 | REST catalog API (not a graphical UI) |
   | SeaweedFS Master | http://localhost:9333 | Cluster/master status |
   | SeaweedFS Volume | http://localhost:8080 | Volume server status |
   | SeaweedFS Filer | http://localhost:8889 | Browse filer namespace |
   | SeaweedFS S3 | http://localhost:8333 | S3 API (not a graphical console) |
   | Spark UI | http://localhost:4040 | Available while a Spark application is running |

   Jupyter token is the value of `JUPYTER_TOKEN` in `.env` (default `lakehouse`).

## Enable `%%sql`

In a notebook cell, run:

```python
%load_ext sql
```

Create a SQLAlchemy connection to Spark's embedded SQL interface using the `ipython-sql` package. For a reliable notebook workflow, use the Spark SQL API directly with `spark.sql("""...""")`; `%%sql` is not automatically a Spark SQL magic just because `ipython-sql` is installed.

For `%%sql` to execute against Spark, register a SQLAlchemy-compatible Spark connection/driver; the `ipython-sql` package alone does not provide a Spark SQLAlchemy dialect. The notebook demonstrates the supported pattern for this lab:

```python
%%sql
SELECT 1;
```

The starter notebook already registers a custom Spark-backed `%%sql` magic. You can use it directly after executing the registration cell.

## Configure Spark + Iceberg REST + SeaweedFS

Open `notebooks/01_pyspark_iceberg_sql.ipynb`. It includes the Spark configuration and a working Spark-backed `%%sql` cell magic. The configuration matches the internal Docker service names.

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("LakehouseLab")
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
    .config("spark.sql.catalog.lake", "org.apache.iceberg.spark.SparkCatalog")
    .config("spark.sql.catalog.lake.type", "rest")
    .config("spark.sql.catalog.lake.uri", "http://iceberg-rest:8181")
    .config("spark.sql.catalog.lake.warehouse", "s3://warehouse/")
    .config("spark.sql.catalog.lake.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
    .config("spark.sql.catalog.lake.s3.endpoint", "http://seaweedfs:8333")
    .config("spark.sql.catalog.lake.s3.path-style-access", "true")
    .config("spark.sql.catalog.lake.s3.access-key-id", "lakehouse")
    .config("spark.sql.catalog.lake.s3.secret-access-key", "lakehouse-secret")
    .config("spark.sql.defaultCatalog", "lake")
    .getOrCreate()
)
```

Then test:

```sql
CREATE NAMESPACE IF NOT EXISTS lake.training;

CREATE TABLE IF NOT EXISTS lake.training.events (
  event_id BIGINT,
  event_type STRING,
  event_date DATE
) USING iceberg;

INSERT INTO lake.training.events VALUES
  (1, 'page_view', DATE'2026-01-01'),
  (2, 'purchase', DATE'2026-01-02');

SELECT * FROM lake.training.events;
```

In Python, execute SQL with `spark.sql("""...""")`.

## `%%sql` caveat and recommended solution

`ipython-sql` is SQLAlchemy/JDBC-oriented and does not automatically submit cells to a SparkSession. The included notebook defines a small custom `%%sql` magic that does.

If you specifically require the literal `%%sql` syntax to run Spark SQL, the clean route is to add **Spark Thrift Server** and connect with a HiveServer2/Thrift SQLAlchemy-compatible driver, or write a small custom IPython cell magic that forwards the cell to `spark.sql`. The latter is a lightweight teaching convenience:

```python
from IPython.core.magic import register_cell_magic

@register_cell_magic
def sql(line, cell):
    return spark.sql(cell).show(truncate=False)

# After running that cell, use:
# %%sql
# SELECT * FROM lake.training.events
```

This custom `%%sql` is Spark SQL-backed and works directly with the SparkSession created above.

## Spark UI

Spark's application UI normally listens on 4040. It is available only while a Spark application is active. If 4040 is occupied, Spark tries 4041, 4042, etc.; Compose publishes 4040-4050. Check:

```powershell
docker compose logs -f jupyter
```

## Useful commands

```powershell
docker compose ps
docker compose logs -f
docker compose down
docker compose down -v   # deletes SeaweedFS persisted data; use carefully
docker compose build --no-cache jupyter
```

## Suggested learning path

1. Object storage: S3 buckets, objects, prefixes, endpoint, path-style access.
2. Iceberg catalog: namespaces, tables, REST API, catalog vs storage.
3. Iceberg table internals: metadata JSON, manifests, data files, snapshots.
4. Spark SQL: create/insert/select, DataFrame API, partitioning.
5. Lakehouse operations: snapshots, time travel, schema evolution, compaction, orphan-file cleanup.
6. Medallion design: Bronze → Silver → Gold with Iceberg tables.

## Troubleshooting

- **Jupyter cannot reach REST**: use `http://iceberg-rest:8181` from containers, not `localhost`.
- **Spark cannot reach S3**: use `http://seaweedfs:8333`, verify the `warehouse` bucket exists and credentials match.
- **Spark UI missing**: run a Spark action (e.g. `df.count()`) and then refresh port 4040.
- **`%%sql` missing**: run the custom `register_cell_magic` cell above. `ipython-sql` does not implement SparkSession integration.
- **No data visible in Windows folder**: the `./notebooks`, `./data`, and `./images` bind mounts are host folders relative to `compose.yaml`; create them beside the compose file before starting if needed.
