{{ config(materialized='table') }}

WITH raw_data AS (
    SELECT * FROM raw.clima_diario
)

SELECT 
    time::DATE as data_previsao,
    temperature_2m_max as temp_max_celsius,
    precipitation_sum as precipitacao_mm,
    CASE 
        WHEN precipitation_sum > 15.0 THEN 'Alerta: Chuva Forte - Risco de Atraso'
        WHEN precipitation_sum > 0 THEN 'Chuva Leve'
        ELSE 'Céu Limpo'
    END as status_operacao
FROM raw_data