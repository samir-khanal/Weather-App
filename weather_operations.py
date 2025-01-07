#import streamlit as st 
import requests
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

#fetching weather data
def weather_data_info(city_name,API_key):
    base_url=f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_key}&units=metric"
    # "metric" is used for celcius whereas
    # "imperial" is used for fahrenheit

    response= requests.get(base_url)

    #weather_info=response.json()
    #print(weather_info)
    if response.status_code==200:
        return response.json()
    else:
        #st.error(f"Error:{response.status_code}")
        return None
#fetch longitude and latitude of city using Openweathermap
def get_city_coordinates(city_name, API_key):
    """
    Fetch latitude and longitude of a city using OpenWeatherMap API.
    """
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_key}"
    response = requests.get(base_url)

    if response.status_code == 200:
        data = response.json()
        return data["coord"]["lat"], data["coord"]["lon"]
    else:
        return None, None
    
# Open-Meteo API: Fetch historical weather data
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

def fetch_historical_weather(city_name, latitude, longitude, start_date, end_date):
    """
    Fetch historical weather data from Open-Meteo API.
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["temperature_2m", "relative_humidity_2m"],
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min"]
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]  # Single location response

    # Process hourly data
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "temperature_2m": hourly_temperature_2m,
        "relative_humidity_2m": hourly_relative_humidity_2m
    }
    hourly_df = pd.DataFrame(hourly_data)
    #renaming the columns
    hourly_df.rename(columns={"temperature_2m": "temperature(in hrs)", "relative_humidity_2m": "humidity(%)"}, inplace=True)

    # Process daily data
    daily = response.Daily()
    daily_weather_code = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_max = daily.Variables(1).ValuesAsNumpy() 
    daily_temperature_min = daily.Variables(2).ValuesAsNumpy() 
    daily_temperature_avg = (daily_temperature_max + daily_temperature_min) / 2

    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        ),
        "weather_code": daily_weather_code,
        "temperature_avg": daily_temperature_avg
    }
    daily_df = pd.DataFrame(daily_data)
    daily_df.rename(columns={"temperature_avg": "Temperature(AVG)"}, inplace=True)

    return hourly_df, daily_df