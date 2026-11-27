from datetime import date, timedelta

import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

# Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
# L'archive a ~5 jours de retard : au-delà on utilise l'API forecast (past_days <= 92)
ARCHIVE_DELAY_DAYS = 5


def fetch_weather_data(latitude, longitude, start_date, end_date,
                       hourly_variables=("temperature_2m",), timezone="UTC",
                       date_format="%Y-%m-%d %H:%M"):
    """
    Récupère la météo horaire pour un lieu et une période.

    Args:
        latitude, longitude: coordonnées du lieu
        start_date, end_date: 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM' (bornes incluses),
            interprétés dans le fuseau `timezone`
        hourly_variables: variable(s) Open-Meteo, ex. ("temperature_2m", "wind_speed_10m")
        timezone: fuseau des timestamps retournés (ex. "UTC", "Europe/Paris")
        date_format: format de la colonne 'date' (sans secondes par défaut) ;
            None pour garder un datetime pandas avec fuseau

    Returns:
        DataFrame avec une colonne 'date' et une colonne par variable
    """
    if isinstance(hourly_variables, str):
        hourly_variables = [hourly_variables]
    hourly_variables = list(hourly_variables)

    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    use_archive = end_ts.date() <= date.today() - timedelta(days=ARCHIVE_DELAY_DAYS)
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_ts.strftime("%Y-%m-%d"),
        "end_date": end_ts.strftime("%Y-%m-%d"),
        "hourly": hourly_variables,
        "timezone": timezone,
    }
    response = openmeteo.weather_api(ARCHIVE_URL if use_archive else FORECAST_URL, params=params)[0]

    hourly = response.Hourly()
    data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )
    }
    # L'ordre des variables doit être le même que dans la requête
    for i, name in enumerate(hourly_variables):
        data[name] = hourly.Variables(i).ValuesAsNumpy()

    df = pd.DataFrame(data)
    if timezone != "UTC":
        df["date"] = df["date"].dt.tz_convert(timezone)
    # Si une heure est précisée, on coupe aux bornes exactes
    start_ts = start_ts.tz_localize(timezone) if start_ts.tzinfo is None else start_ts
    end_ts = end_ts.tz_localize(timezone) if end_ts.tzinfo is None else end_ts
    if len(str(end_date).strip()) <= 10:
        end_ts = end_ts + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    df = df[(df["date"] >= start_ts) & (df["date"] <= end_ts)].reset_index(drop=True)
    if date_format:
        df["date"] = df["date"].dt.strftime(date_format)
    return df

def save_to_csv(df, filename='weather_data.csv'):
    """Sauvegarde les données en CSV"""
    if not df.empty:
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Données sauvegardées dans {filename}")
    else:
        print("Pas de données à sauvegarder")

if __name__ == "__main__":
    # Paris
    df = fetch_weather_data(48.8566, 2.3522, "2026-11-01", "2026-11-15",
                            hourly_variables=["temperature_2m"])
    print(df)

    if not df.empty:
        save_to_csv(df)
