import streamlit as st
from streamlit_js_eval import streamlit_js_eval
from weather_radar import show_weather_radar
from weather_ui import show_title, show_log_window
from weather_api import load_city_map
from weather_card import weather_card
from weather_weekly import weekly_weather_card

show_title()
city_map = load_city_map()
korean_cities = list(city_map.keys())
# (기상 레이더, get_weather_by_method 등 기존 함수는 별도 파일에서 관리)
show_log_window()

