
import requests
import os
import json
import streamlit as st
API_KEY = st.secrets["openweathermap"]["api_key"]
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def load_city_map():
    with open('city_map.json', encoding='utf-8') as f:
        return json.load(f)

def get_weather_data(city_map, city_name, api_key, base_url):
    city_eng = city_map.get(city_name, city_name)
    if city_name == "김포":
        lat, lon = 37.6153, 126.7159
        url = f"{base_url}?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    else:
        url = f"{base_url}?q={city_eng}&appid={api_key}&units=metric&lang=kr"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"[{city_name}] 날씨 정보를 가져올 수 없습니다. (상태 코드: {response.status_code})")
        return None

def get_weekly_forecast(data, api_key):
    lat, lon = data['coord']['lat'], data['coord']['lon']
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&lang=kr&appid={api_key}"
    resp_forecast = requests.get(forecast_url)
    if resp_forecast.status_code == 200:
        forecast_data = resp_forecast.json()
        return forecast_data.get('list', [])
    else:
        st.warning("주간 날씨 정보를 가져올 수 없습니다.")
        return []
