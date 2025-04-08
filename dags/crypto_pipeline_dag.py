from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

with DAG(
    dag_id='crypto_pipeline_dag',
    default_args=default_args,
    description='A simple crypto pipeline DAG',
    schedule_interval=None,
    catchup=False,
) as dag:

    ingest_task = BashOperator(
        task_id='ingest_data',
        bash_command='python /opt/airflow/scripts/ingest.py',
    )

    transform_task = BashOperator(
        task_id='transform_data',
        bash_command='python /opt/airflow/scripts/transform.py',
    )

    ingest_task >> transform_task
