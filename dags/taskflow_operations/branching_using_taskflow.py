import pandas as pd

from airflow.utils.dates import days_ago

from airflow.models import Variable
from airflow.decorators import dag, task
from airflow.operators.python import PythonOperator


default_args = {
    'owner' : 'airflow'
}


@dag(
    dag_id='branching_using_taskflow',
    description = 'Branching using taskflow',
    default_args = default_args,
    start_date = days_ago(1),
    schedule_interval = '@once',
    tags = ['branching', 'python', 'taskflow']
)
def branching_using_taskflow():

    @task(task_id='read_csv_file_task')
    def read_csv_file():
        df = pd.read_csv('/opt/airflow/datasets/car_data.csv')

        print(df)

        return df.to_json()


    @task.branch
    def determine_branch():
        final_output = Variable.get("transform", default_var=None)

        if final_output == 'filter_two_seaters':
            return 'filter_two_seaters_task'
        elif final_output == 'filter_fwds':
            return 'filter_fwds_task'


    @task(task_id='filter_two_seaters_task')
    def filter_two_seaters(**kwargs):
        ti = kwargs['ti']
        json_data = ti.xcom_pull(task_ids='read_csv_file_task')
    
        df = pd.read_json(json_data)
        
        two_seater_df = df[df['Seats'] == 2]
        
        ti.xcom_push(key='transform_result', value=two_seater_df.to_json())
        ti.xcom_push(key='transform_filename', value='two_seaters')


    @task(task_id='filter_fwds_task')
    def filter_fwds(**kwargs):
        ti = kwargs['ti']
        json_data = ti.xcom_pull(task_ids='read_csv_file_task')
    
        df = pd.read_json(json_data)
        
        fwd_df = df[df['PowerTrain'] == 'FWD']
        
        ti.xcom_push(key='transform_result', value=fwd_df.to_json())
        ti.xcom_push(key='transform_filename', value='fwds')

    @task(trigger_rule='none_failed')
    def write_csv_result(**kwargs): 
        ti = kwargs['ti']

        json_data = ti.xcom_pull(key='transform_result')
        file_name = ti.xcom_pull(key='transform_filename')

        df = pd.read_json(json_data)

        df.to_csv(
            '/opt/airflow/outputs/{0}.csv'.format(file_name), index=False)


    read_csv_file() >> determine_branch() >> [
        filter_two_seaters(), 
        filter_fwds()
    ] >> write_csv_result()


branching_using_taskflow()




