from datetime import datetime

from airflow import DAG
from airflow.sensors.filesystem import FileSensor


default_args = {
   'owner': 'airflow'
}

with DAG(
    dag_id='simple_file_sensor',
    description='Running a simple file sensor',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule='@once',
    tags=['python', 'sensor', 'file sensor'],
) as dag:

    checking_for_file = FileSensor(
        task_id = 'checking_for_file',
        filepath = '/opt/airflow/datasets/sensor_target.csv',
        poke_interval = 10,
        timeout = 60 * 10
    )


checking_for_file
