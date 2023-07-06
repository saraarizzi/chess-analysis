from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# from api_statistics import StatisticsUpdater

default_args = {
    'owner': 'API',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}


def start():
    print(f"Started at {datetime.now()}")


def end():
    print(f"Finished at {datetime.now()}")


def get_stats():
    pass
    # StatisticsUpdater().update_stats()


with DAG(
        default_args=default_args,
        dag_id='dag_stats_daily',
        description='Used to retrieve data from chess.com Matches API',
        start_date=datetime(year=2023, month=6, day=15),
        schedule_interval='30 00 * * *'
) as dag:

    task1 = PythonOperator(
        task_id='start',
        python_callable=start
    )

    task2 = PythonOperator(
        task_id='get_stats',
        python_callable=get_stats
    )

    task3 = PythonOperator(
        task_id='end',
        python_callable=end
    )

    task1 >> task2 >> task3
