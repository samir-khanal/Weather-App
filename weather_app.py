import streamlit as st 
from weather_operations import weather_data_info, fetch_historical_weather, get_city_coordinates
from store_api import API_KEY
import pandas as pd 
from datetime import datetime
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')

Searched_cities="searched_cities.csv"

def store_weather_data(city_name, weather_data):
    # Current date and day
    current_date = datetime.now().date() # datetime.now() it gets current date and time
    current_day = datetime.now().strftime("%A") #strftime "string format time" and %A return full name of the current day

    #checking if file exists or not.
    try:
        searched_cities_df=pd.read_csv(Searched_cities)
    except FileNotFoundError:
        # if file does not exist then create a new dataframe
        searched_cities_df=pd.DataFrame(columns=["city", "temperature(Celsius)", "humidity", "description","Date","Day"])
        #checking if the city already exist in the file
    if city_name.lower() in searched_cities_df["city"].str.lower().values:
        # if city already exists, update the data...
        searched_cities_df.loc[searched_cities_df["city"].str.lower() == city_name.lower(), "temperature(Celsius)"] = weather_data["main"]["temp"]
        searched_cities_df.loc[searched_cities_df["city"].str.lower() == city_name.lower(), "humidity"] = weather_data["main"]["humidity"]
        searched_cities_df.loc[searched_cities_df["city"].str.lower() == city_name.lower(), "description"] = weather_data["weather"][0].get("description", "unknown")
        searched_cities_df.loc[searched_cities_df["city"].str.lower() == city_name.lower(), "Date"] = current_date
        searched_cities_df.loc[searched_cities_df["city"].str.lower() == city_name.lower(), "Day"] = current_day
        searched_cities_df.to_csv(Searched_cities, index=False)
        return "updated"
        #return False # city already exists..
    else:
        #if city doesnot exist adding a new row..
        temp= weather_data["main"]["temp"]
        humidity= weather_data["main"]["humidity"]
        description= weather_data["weather"][0].get("description","unknown")

        # append the new city
        new_data = pd.DataFrame({"city": [city_name],"temperature(Celsius)": [temp],"humidity": [humidity],"description": [description],"Date": [current_date],"Day": [current_day]})
        #adding/append the new_data to existing DataFrame
        searched_cities_df = pd.concat([searched_cities_df, new_data], ignore_index=True)
        searched_cities_df.to_csv(Searched_cities, index=False)
        return "stored"
    
# .........Streamlit UI...............
st.markdown("<h1 style='text-align: center;'>WEATHER APP</h1>",unsafe_allow_html=True)

# CURRENT WEATHER(OpenWeatherMap)
st.subheader("🌦️Get Current Weather Details")
st.write("Enter a city name to get current weather details")
city=st.text_input("City Name ",placeholder="Enter a city name")

if st.button("Get Weather Details",type="primary", key="current_weather"):
    if city:
        weather_data= weather_data_info(city,API_KEY)

        if weather_data:
            st.success(f"🌍Current Weather Details for **{city.upper()}**:")
            temp= weather_data["main"]["temp"]
            st.write(f"🌡️Temperature is: {temp}°C")

            humidity=weather_data["main"]["humidity"]
            st.write(f"💧Humidity: {humidity}%")

            description = weather_data["weather"][0]["description"].upper()
            st.write(f" condition: {description}")

            # storing the searched cities in the csv file
            result = store_weather_data(city,weather_data)
            if result == "stored":
                st.info(f"the data of {city.upper()} has been stored.✅")
            else:
                st.info(f"The data of {city.upper()} has been updated.🔄")
        else:
            st.error("❌City not found! please enter correct city name!")    

    else:
        st.error("please enter a city name!!")

# Add Search History Panel
st.divider()
st.subheader("Search History")

if st.checkbox("Show Search History"):
    try:
        searched_cities_df = pd.read_csv(Searched_cities)
        searched_cities_df['Date'] = pd.to_datetime(searched_cities_df['Date'])
        searched_cities_df['Day'] = searched_cities_df['Date'].dt.day_name()
        st.dataframe(searched_cities_df[['city', 'temperature(Celsius)', 'humidity', 'Date', 'Day']])
    except FileNotFoundError:
        st.info("No search history found.")

#Historical Weather(Open-Meteo)   
st.divider()    

st.subheader("Fetch Historical Weather Data")

if city:
    # st.info(f"fetching coordinates for {city.upper()}....")
# latitude = st.number_input("Enter Latitude:", min_value=-90.0, max_value=90.0, value=0.0)
# longitude = st.number_input("Enter Longitude:", min_value=-180.0, max_value=180.0, value=0.0)
    latitude, longitude = get_city_coordinates(city, API_KEY)
    if latitude is not None and longitude is not None:
        st.success(f"📍Coordinates for {city.upper()}: Latitude {latitude}, Longitude {longitude}")
    else:
        st.error("⚠️Failed to fetch coordinates. Please check the city name.")
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
        hourly_df['date'] = pd.to_datetime(hourly_df['date']) 
        # Method used:plt.subplots():when need more control over plot elements and working on large,professional visualizational project.
        fig, ax = plt.subplots()
        hourly_df.set_index("date")["temperature(in hrs)"].plot(ax=ax, color='blue')
        # default would set as line chart whereas to chage it we use ex: kind="bar"
        ax.set_title("Hourly Temperature Trend", fontsize=14)
        ax.set_xlabel("Date and Time")
        ax.set_ylabel("Temperature (°C)")
        st.pyplot(fig)

        # Method used: plt.figure() with plt.plot()
        # fig = plt.figure()  # Create a new figure
        # plt.plot(hourly_df["date"], hourly_df["temperature(in hrs)"], color='blue')
        # plt.title("Hourly Temperature Trend", fontsize=14)  # Add a title
        # plt.xlabel("Date and Time")  # x-axis label
        # plt.ylabel("Temperature (°C)")  # y-axis label
        # plt.xticks(rotation=45)  # rotate x-axis labels
        # st.pyplot(fig)  # Display the figure in Streamlit

        # direct way to plot linechart in streamlit
        #st.line_chart(hourly_df.set_index("date")["temperature(in hrs)"]) 

        st.write("### Daily Weather Codes")
        daily_df['date'] = pd.to_datetime(daily_df["date"]).dt.date
        fig, ax = plt.subplots()
        daily_df.set_index("date")["weather_code"].plot(kind="bar", ax=ax, color='red')
        ax.set_title("Daily Weather Codes", fontsize=14)
        ax.set_xlabel("Date")
        #ax.set_xticklabels(daily_df['date'], rotation=90, ha='right')
        ax.set_ylabel("Weather Code")
        ax.set_xticks(range(len(daily_df))) 
        ax.set_xticklabels(daily_df["date"], rotation=0, ha="center")
        st.pyplot(fig)
        
        #st.bar_chart(daily_df.set_index("date")["weather_code"])
    else:
        st.error("Please provide all required inputs!") 

# compare weather between two cities
st.divider()
st.subheader("🌍 Compare Weather Between Two Cities")

city1 = st.text_input("Enter the first city", placeholder="Enter the first city", key="city1")
city2 = st.text_input("Enter the second city", placeholder="Enter the second city", key="city2")

if st.button("Compare Weather", key="compare_weather"):
    if city1 and city2:
        weather1 = weather_data_info(city1, API_KEY)
        weather2 = weather_data_info(city2, API_KEY)

        if weather1 and weather2:
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**{city1.upper()}**")
                st.write(f"🌡️ Temperature: {weather1['main']['temp']}°C")
                st.write(f"💧 Humidity: {weather1['main']['humidity']}%")
                st.write(f"📄 Condition: {weather1['weather'][0]['description'].capitalize()}")

            with col2:
                st.write(f"**{city2.upper()}**")
                st.write(f"🌡️ Temperature: {weather2['main']['temp']}°C")
                st.write(f"💧 Humidity: {weather2['main']['humidity']}%")
                st.write(f"📄 Condition: {weather2['weather'][0]['description'].capitalize()}")
        else:
            st.error("cities not found! Please enter valid city names.")
    else:
        st.warning("Please enter both city names for comparison.")
# KEY NOTES
# 1) MATPLOTLIB:
# Use plt.subplots() when:
# You need to create multiple plots in one figure.
# You require advanced control over plot elements.
# You’re working on a large, professional visualization project.
# Use plt.figure() with plt.plot() when:
# You need a simple, quick plot.
# You don’t need multiple plots or advanced features.
