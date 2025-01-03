import streamlit as st 
from weather_operations import weather_data_info
from store_api import API_KEY

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
        else:
            st.error("City not found! please enter correct city name!")    

    else:
        st.error("please enter a city name!!")
