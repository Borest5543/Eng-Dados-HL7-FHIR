from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime

with DAG(
    dag_id="dag_patient_ingest_spark",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    spark_task = SparkSubmitOperator(
        task_id="spark_patient_ingest_task",
        application="/opt/spark_app/patient_ingest.py",
        conn_id="spark_default",  # usa a conexão configurada no Airflow
        verbose=True,
        application_args=["file:///opt/data/patients.csv"],
        name="FHIR_Patient_Ingestion",
    )


    spark_task
