# Convert this file to a notebook cell-by-cell, or run it as a script.
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
spark.sql("CREATE NAMESPACE IF NOT EXISTS lake.demo")
spark.sql("""
CREATE TABLE IF NOT EXISTS lake.demo.customers (
  customer_id BIGINT,
  customer_name STRING,
  country STRING
) USING iceberg
""")
spark.sql("""
INSERT INTO lake.demo.customers VALUES
 (1, 'Amina', 'Morocco'),
 (2, 'Youssef', 'Morocco'),
 (3, 'Sara', 'France')
""")
spark.sql("SELECT * FROM lake.demo.customers").show()
