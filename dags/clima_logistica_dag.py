from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import requests
import pandas as pd
from sqlalchemy import create_engine

# Conexão com o Postgres
engine = create_engine('postgresql://airflow:airflow_password@postgres:5432/portfolio_db')

def extract_and_load():
    # Coordenadas de SP (região Faria Lima)
    url = "https://api.open-meteo.com/v1/forecast?latitude=-23.58&longitude=-46.68&daily=temperature_2m_max,precipitation_sum&timezone=America%2FSao_Paulo"
    response = requests.get(url).json()
    
    # Tratamento básico com Pandas
    df = pd.DataFrame(response['daily'])
    df['extraction_date'] = datetime.now()
    
    # Carregando no schema raw (cria a tabela se não existir)
    engine.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    df.to_sql('clima_diario', engine, schema='raw', if_exists='replace', index=False)

default_args = {
    'owner': 'data_engineer',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'pipeline_clima_operacional',
    default_args=default_args,
    start_date=datetime(2026, 10, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:

    ingestao_api = PythonOperator(
        task_id='extrair_dados_openmeteo',
        python_callable=extract_and_load
    )

    # Executa o dbt para transformar o dado bruto em analítico
    transformacao_dbt = BashOperator(
        task_id='transformar_dados_dbt',
        bash_command='cd /opt/airflow/dbt_weather && dbt run --profiles-dir .'
    )

    ingestao_api >> transformacao_dbt