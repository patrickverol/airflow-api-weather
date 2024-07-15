# Project ELT Weather- Data extraction from API with Apache Airflow

# Imports
import datetime as dt
from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from airflow.utils.dates import days_ago
from project_etl import etl_weather

# Arguments
default_args ={
    'owner':'Patrick Verol',
    'depends_on_past':False,
    'start_date':dt.datetime.today(),
    'retries':1,
    'retry_delay':timedelta(minutes=1)
}

# DAG
dsa_dag = DAG('project_dag_weather',
              default_args = default_args,
              description = 'Project API Weather',
              schedule_interval = timedelta(minutes=60)
)

# Python Operator
execute_etl = PythonOperator(task_id = 'project_etl_weather',
                             python_callable = etl_weather,
                             dag = dsa_dag
)

# Send the task for execution
execute_etl