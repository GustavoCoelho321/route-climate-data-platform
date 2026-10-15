import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(page_title="Dashboard Operacional", layout="wide")

# Conectando ao banco (localhost porque rodará fora da rede do docker-compose para facilitar)
engine = create_engine('postgresql://airflow:airflow_password@localhost:5432/portfolio_db')

st.title("Painel de Controle: Clima & Operações")

try:
    df = pd.read_sql("SELECT * FROM analytics.stg_clima_alertas", engine)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Previsão de Temperatura")
        st.line_chart(df.set_index('data_previsao')['temp_max_celsius'])
    
    with col2:
        st.subheader("Alertas de Roteirização (Precipitação)")
        st.dataframe(df[['data_previsao', 'status_operacao', 'precipitacao_mm']])
        
except Exception as e:
    st.warning("Aguardando a execução do pipeline no Airflow para gerar os dados analíticos...")