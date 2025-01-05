import streamlit as st 
from weather_operations import weather_data_info
from store_api import API_KEY
import pandas as pd 

Searched_cities="searched_cities.csv"

def store_weather_data(city_name, weather_data):
    #checking if file exists or not.
    try:
        searched_cities_df=pd.read_csv(Searched_cities)
    except FileNotFoundError:
        # if file does not exist then create a new dataframe
        searched_cities_df=pd.DataFrame(columns=["city", "temperature(Celsius)", "humidity", "description"])
        #checking if the city already exist in the file
    if city_name.lower() in searched_cities_df["city"].str.lower().values:
        # if city already exists, update the data...
        searched_cities_df.loc[searched_cities_df["city"].str.lower() == city_name.lower(), "temperature(Celsius)"] = weather_data["main"]["temp"]
        searched_cities_df.loc[searched_cities_df["city"].str.lower() == city_name.lower(), "humidity"] = weather_data["main"]["humidity"]
        searched_cities_df.loc[searched_cities_df["city"].str.lower() == city_name.lower(), "description"] = weather_data["weather"][0].get("description", "unknown")

        searched_cities_df.to_csv(Searched_cities, index=False)
        return "updated"
        #return False # city already exists..
    else:
        #if city doesnot exist adding a new row..
        temp= weather_data["main"]["temp"]
        humidity= weather_data["main"]["humidity"]
        description= weather_data["weather"][0].get("description","unknown")

        # append the new city
        new_data = pd.DataFrame({"city": [city_name],"temperature(Celsius)": [temp],"humidity": [humidity],"description": [description]})
        #adding/append the new_data to existing DataFrame
        searched_cities_df = pd.concat([searched_cities_df, new_data], ignore_index=True)
        searched_cities_df.to_csv(Searched_cities, index=False)
        return "stored"
    
# .........Streamlit UI...............
st.markdown("<h1 style='text-align: center;'>WEATHER APP</h1>",unsafe_allow_html=True)

st.write("Enter a city name to get current weather details")
city=st.text_input("City Name ",placeholder="Enter a city name", )

if st.button("Get Weather Details",type="primary"):
    if city:
        weather_data= weather_data_info(city,API_KEY)

        if weather_data:
            st.success(f"Current Weather Details of {city.upper()}:")
            temp= weather_data["main"]["temp"]
            st.write(f"Temperature is: {temp}°C")

            humidity=weather_data["main"]["humidity"]
            st.write(f"Humidity: {humidity}")

            description = weather_data["weather"][0]["description"].upper()
            st.write(f" condition: {description}")

            # storing the searched cities in the csv file
            result = store_weather_data(city,weather_data)
            if result == "stored":
                st.info(f"the data of {city.upper()} has been stored.")
            else:
                st.info(f"The data of {city.upper()} has been updated.")
        else:
            st.error("City not found! please enter correct city name!")    

    else:
        st.error("please enter a city name!!")
