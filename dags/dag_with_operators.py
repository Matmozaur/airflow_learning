import time
from datetime import datetime

from airflow import DAG
from airflow.operators.python_operator import PythonOperator


# Define default arguments for DAG
default_args = {
    'start_date': datetime(2023, 10, 13),
    'retries': 2,
}

def task_a():
    print('a')

def task_b():
    time.sleep(3)
    print('b')


def task_c():
    time.sleep(3)
    print('c')


def task_d():
    time.sleep(3)
    print('d')

# Define DAG
with DAG('dag_with_operators', default_args=default_args, schedule_interval='0 0 * * *', catchup=False) as dag:
    taskA = PythonOperator(task_id='A', python_callable=task_a)
    taskB = PythonOperator(task_id='B', python_callable=task_b)
    taskC = PythonOperator(task_id='C', python_callable=task_c)
    taskD = PythonOperator(task_id='D', python_callable=task_d)

    # Set task dependencies
    taskA >> [taskB, taskC] >> taskD
