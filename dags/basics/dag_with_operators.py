import time
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


# Define default arguments for DAG
default_args = {
    'start_date': datetime(2024, 1, 1),
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

def task_e():
    time.sleep(3)
    print('e')


def task_f():
    time.sleep(3)
    print('f')


def task_g():
    time.sleep(3)
    print('g')

# Define DAG
with DAG('dag_with_operators', default_args=default_args, schedule='0 0 * * *', catchup=False) as dag:
    task_a_op = PythonOperator(task_id='A', python_callable=task_a)
    task_b_op = PythonOperator(task_id='B', python_callable=task_b)
    task_c_op = PythonOperator(task_id='C', python_callable=task_c)
    task_d_op = PythonOperator(task_id='D', python_callable=task_d)
    task_e_op = PythonOperator(task_id='E', python_callable=task_e)
    task_f_op = PythonOperator(task_id='F', python_callable=task_f)
    task_g_op = PythonOperator(task_id='G', python_callable=task_g)

    # Set task dependencies
    [[task_a_op, task_b_op] >> task_e_op, [task_c_op, task_d_op] >> task_f_op] >> task_g_op
