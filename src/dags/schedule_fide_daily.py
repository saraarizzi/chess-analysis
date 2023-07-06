from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.scraping.scraping_fide import FIDEScraper

default_args = {
    'owner': 'Scraper',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}


def start():
    print(f"Started at {datetime.now()}")


def end():
    print(f"Finished at {datetime.now()}")


def scrape_fide():
    FIDEScraper().scrape_fide()


with DAG(
        default_args=default_args,
        dag_id='dag_fide_daily',
        description='Used to scrape FIDE.com Player Ratings',
        start_date=datetime(year=2023, month=6, day=15),
        schedule_interval='30 00 * * *'
) as dag:

    task1 = PythonOperator(
        task_id='start',
        python_callable=start
    )

    task2 = PythonOperator(
        task_id='scrape_fide',
        python_callable=scrape_fide
    )

    task3 = PythonOperator(
        task_id='end',
        python_callable=end
    )

    task1 >> task2 >> task3
