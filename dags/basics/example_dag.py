from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

def print_hello():
    return 'Hello world!'

# Define default arguments for DAG
default_args = {
    'start_date': datetime(2023, 10, 13),
    'retries': 2,
}

# Define DAG
with DAG('example_dag', default_args=default_args, schedule_interval='@daily', catchup=False) as dag:
    start = DummyOperator(task_id='start')
    hello_task = PythonOperator(task_id='hello_task', python_callable=print_hello)
    end = DummyOperator(task_id='end')

    # Set task dependencies
    start >> hello_task >> end
