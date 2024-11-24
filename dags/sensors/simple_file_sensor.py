from datetime import datetime, timedelta
from airflow.utils.dates import days_ago
import pandas as pd

from airflow import DAG

from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor


default_args = {
   'owner': 'airflow'
}

with DAG(
    dag_id = 'simple_file_sensor',
    description = 'Running a simple file sensor',
    default_args = default_args,
    start_date = days_ago(1),
    schedule_interval = '@once',
    tags = ['python', 'sensor', 'file sensor'],
) as dag:

    checking_for_file = FileSensor(
        task_id = 'checking_for_file',
        filepath = '/opt/airflow/datasets/sensor_target.csv',
        poke_interval = 10,
        timeout = 60 * 10
    )


checking_for_file
