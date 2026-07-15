from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

def print_hello():
    return 'Hello world!'

# Define default arguments for DAG
default_args = {
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
}

# Define DAG
with DAG('example_dag', default_args=default_args, schedule='@daily', catchup=False) as dag:
    start = EmptyOperator(task_id='start')
    hello_task = PythonOperator(task_id='hello_task', python_callable=print_hello)
    end = EmptyOperator(task_id='end')

    # Set task dependencies
    start >> hello_task >> end
