# electricity-forecasting-mlops

End-to-end MLOps pipeline to forecast French electricity consumption (RTE eCO2mix + weather): Airflow orchestration, Polars/DuckDB processing, data quality checks, XGBoost/SARIMA time series models, MLflow tracking, FastAPI serving with Docker, drift monitoring.


## Source des données 

- RTE eCO2mix : https://www.rte-france.com/donnees-publications/eco2mix-donnees-temps-reel
reel time data on electric, we will check the dataset of 5 years 
- 