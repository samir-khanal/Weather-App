#import streamlit as st 
import requests
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