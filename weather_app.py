import streamlit as st 
from weather_operations import weather_data_info, fetch_historical_weather, get_city_coordinates
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

# CURRENT WEATHER(OpenWeatherMap)
st.subheader("Get Current Weather Details")
st.write("Enter a city name to get current weather details")
city=st.text_input("City Name ",placeholder="Enter a city name", )

if st.button("Get Weather Details",type="primary", key="current_weather"):
    if city:
        weather_data= weather_data_info(city,API_KEY)

        if weather_data:
            st.success(f"Current Weather Details of {city.upper()}:")
            temp= weather_data["main"]["temp"]
            st.write(f"Temperature is: {temp}°C")

            humidity=weather_data["main"]["humidity"]
            st.write(f"Humidity: {humidity}%")

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

#Historical Weather(Open-Meteo)       

st.subheader("Fetch Historical Weather Data")

if city:
    # st.info(f"fetching coordinates for {city.upper()}....")
# latitude = st.number_input("Enter Latitude:", min_value=-90.0, max_value=90.0, value=0.0)
# longitude = st.number_input("Enter Longitude:", min_value=-180.0, max_value=180.0, value=0.0)
    latitude, longitude = get_city_coordinates(city, API_KEY)
    if latitude is not None and longitude is not None:
        st.success(f"Coordinates for {city.upper()}: Latitude {latitude}, Longitude {longitude}")
    else:
        st.error("Failed to fetch coordinates. Please check the city name.")
else:
    st.warning("Enter a city name in the Current Weather section to fetch coordinates.")

#input historical weather
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

if st.button("Fetch Historical Weather", key="historical_weather"):
    if latitude and longitude and start_date and end_date:
        hourly_df, daily_df = fetch_historical_weather(city, latitude, longitude, start_date, end_date)
        st.success("Historical Weather Data Fetched Successfully!")

        # Add weather code descriptions
        weather_code_map = {
            0: "☀️Clear sky",
            1: "🌤️ Mainly clear",
            2: "⛅ Partly cloudy",
            3: "☁️ Overcast",
            45: "🌫️ Fog",
            48: "🌫️ Depositing rime fog",
            51: "🌦️ Drizzle: Light",
            53: "🌦️ Drizzle: Moderate",
            55: "🌦️ Drizzle: Dense",
            61: "🌧️ Rain: Slight",
            63: "🌧️ Rain: Moderate",
            65: "🌧️ Rain: Heavy",
            66: "🌨️ Freezing Rain: Light",
            67: "🌨️ Freezing Rain: Heavy",
            71: "❄️ Snowfall: Slight",
            73: "❄️ Snowfall: Moderate",
            75: "❄️ Snowfall: Heavy",
            80: "🌧️ Rain Showers: Slight",
            81: "🌧️ Rain Showers: Moderate",
            82: "🌧️ Rain Showers: Violent",
            95: "⛈️ Thunderstorm: Slight",
            96: "⛈️ Thunderstorm with hail",
        }
        daily_df["weather_description"] = daily_df["weather_code"].map(weather_code_map)

        st.write("### Hourly Weather Data")
        st.dataframe(hourly_df)

        st.write("### Daily Weather Data")
        st.dataframe(daily_df)

        st.write("### Hourly Temperature Trend")
        st.line_chart(hourly_df.set_index("date")["temperature(in hrs)"])

        st.write("### Daily Weather Codes")
        st.bar_chart(daily_df.set_index("date")["weather_code"])
    else:
        st.error("Please provide all required inputs!") 
