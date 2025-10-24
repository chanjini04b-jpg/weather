# 실시간 기상 레이더 지도 API 예시 (OpenWeatherMap Weather Layers)
# Streamlit에서 leaflet.js 기반 지도와 OpenWeatherMap weather layer를 표시하는 코드 예시
import streamlit as st
import streamlit.components.v1 as components

def show_weather_radar(center_lat=None, center_lon=None):
    st.markdown("<h3>🌧️ 실시간 기상 레이더 지도</h3>", unsafe_allow_html=True)
    # 기본 좌표(한국 중심)
    lat = center_lat if center_lat is not None else 36.5
    lon = center_lon if center_lon is not None else 127.8
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
      // 내 위치 마커
      L.marker([{lat}, {lon}]).addTo(map).bindPopup('내 위치').openPopup();
    </script>
    '''
    components.html(leaflet_html, height=420)
