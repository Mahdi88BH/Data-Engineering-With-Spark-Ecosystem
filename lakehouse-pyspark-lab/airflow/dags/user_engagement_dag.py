from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.trino.hooks.trino import TrinoHook
from airflow.providers.smtp.operators.smtp import EmailOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

def upload_csv_to_seaweedfs(**context):
    ds = context['ds']
    local_file_path = f"/tmp/segmented_users_{ds}.csv"
    object_name = f"segment_users/segmented_users_{ds}.csv"
    bucket_name = "customer-segments"
    
    # Configuration pour SeaweedFS (S3 compatible)
    s3_client = boto3.client(
        's3',
        endpoint_url='http://seaweedfs:8333',
        aws_access_key_id='lakehouse',
        aws_secret_access_key='lakehouse-secret',
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )

    # Vérifier si le bucket existe, sinon le créer (logique corrigée)
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} created.")

    # Upload du fichier
    s3_client.upload_file(local_file_path, bucket_name, object_name)
    print(f"✅ Uploaded {local_file_path} to s3://{bucket_name}/{object_name}")

    # Push path to XCom if needed downstream
    context['ti'].xcom_push(key='s3_path', value=f"s3://{bucket_name}/{object_name}")
    
def export_segmented_users_to_csv(**context):
    ds = context['ds']
    output_path = f"/tmp/segmented_users_{ds}.csv"

    query = """
        SELECT user_id, email, full_name, total_pageviews, active_days,
               last_active_date, days_since_last_active, engagement_segment
        FROM iceberg.gold.user_engagement_segments
    """

    trino_hook = TrinoHook(trino_conn_id='trino_default')
    
    # Récupération des données (nécessite pandas)
    df = trino_hook.get_pandas_df(sql=query)

    df.to_csv(output_path, index=False)
    context['ti'].xcom_push(key='csv_path', value=output_path)

with DAG(
    dag_id="user_engagement_segments_dag", 
    start_date=datetime(2023,1,1), 
    schedule_interval='@daily',
    catchup=False,
    template_searchpath=['/opt/airflow/dags'],   # ← AJOUT
    tags=["gold", "segmentation"]
) as dag:
    
    segment_users = SQLExecuteQueryOperator(
        task_id='segment_users',
        sql='sql/trino.sql',
        conn_id='trino_default',          # ← 'conn_id' au lieu de 'trino_conn_id'
    )
    
    export_csv = PythonOperator(
        task_id='export_to_csv',
        python_callable=export_segmented_users_to_csv,
    )
    
    upload_to_seaweedfs = PythonOperator(
        task_id='upload_to_seaweedfs',
        python_callable=upload_csv_to_seaweedfs,
    )
    
    notify_success = EmailOperator(
        task_id='notify_success',
        from_email='airflow@example.com',   # ← LA LIGNE À AJOUTER
        to='marketing-team@example.com',
        subject='[Airflow] User Engagement Segments Exported',
        html_content="""
            <p>Hello Team,</p>
            <p>The user engagement segments have been refreshed and exported to a CSV file.</p>
            <p>File location: <code>s3://customer-segments/segment_users/segmented_users_{{ ds }}.csv</code></p>
            <p>– Airflow Bot</p>
        """
    )
    
    segment_users >> export_csv >> upload_to_seaweedfs >> notify_success