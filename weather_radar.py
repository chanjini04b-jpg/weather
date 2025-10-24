# 실시간 기상 레이더 지도 API 예시 (OpenWeatherMap Weather Layers)
# Streamlit에서 leaflet.js 기반 지도와 OpenWeatherMap weather layer를 표시하는 코드 예시
import streamlit as st
import streamlit.components.v1 as components

import requests
def show_weather_radar(center_lat=None, center_lon=None):
    st.markdown("<h3>🌧️ 실시간 기상 레이더 지도</h3>", unsafe_allow_html=True)
    # 기본 좌표(한국 중심)
    lat = center_lat if center_lat is not None else 36.5
    lon = center_lon if center_lon is not None else 127.8
    city_name = "내 위치"
    # reverse geocoding으로 도시명 추출
    if center_lat is not None and center_lon is not None:
        try:
            nominatim_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
            nomi_resp = requests.get(nominatim_url, headers={"User-Agent": "weather-app"}, timeout=5)
            if nomi_resp.status_code == 200:
                nomi_data = nomi_resp.json()
                address = nomi_data.get('address', {})
                city_name = address.get('city') or address.get('town') or address.get('village') or address.get('state') or "내 위치"
        except Exception:
            pass
    leaflet_html = f'''
    <div id="map" style="height:400px; width:100%; border-radius:1rem; box-shadow:0 2px 8px #0002;"></div>
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <script>
      var map = L.map('map').setView([{lat}, {lon}], 8);
      L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
        maxZoom: 18,
        attribution: '© OpenStreetMap'
      }}).addTo(map);
      // OpenWeatherMap Weather Layer (precipitation)
      L.tileLayer('https://tile.openweathermap.org/map/precipitation_new/{{z}}/{{x}}/{{y}}.png?appid={st.secrets["openweathermap"]["api_key"]}', {{
        maxZoom: 18,
        opacity: 0.6
      }}).addTo(map);
      // 내 위치 마커에 도시명 표시
      L.marker([{lat}, {lon}]).addTo(map).bindPopup('{city_name}').openPopup();
    </script>
    '''
    components.html(leaflet_html, height=420)
