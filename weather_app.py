import streamlit as st
import requests
import os
from streamlit_js_eval import streamlit_js_eval
from weather_radar import show_weather_radar
# 로그 저장용 리스트
if 'weather_logs' not in st.session_state:
    st.session_state.weather_logs = []
# 현대적 날씨 카드 UI, 아이콘, 배경색 등 추가

# [보안] API 키는 코드에 직접 입력하지 마세요!
# 반드시 .streamlit/secrets.toml 파일에 아래와 같이 저장하세요:
# [openweathermap]
# api_key = "YOUR_API_KEY_HERE"
API_KEY = st.secrets["openweathermap"]["api_key"]
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
# API 연결 성공 여부 상단 표시
def check_api_connection():
    test_url = f"{BASE_URL}?q=Seoul&appid={API_KEY}&units=metric&lang=kr"
    try:
        response = requests.get(test_url, timeout=5)
        if response.status_code == 200:
            st.success("✅ OpenWeather API 연결 성공!")
        elif response.status_code == 401:
            st.error("❌ API 키 오류: 올바르지 않거나 활성화되지 않았습니다.")
        else:
            st.warning(f"⚠️ API 연결 상태: {response.status_code}")
    except Exception as e:
        st.error(f"❌ API 연결 실패: {e}")

# 내 위치 연결 상태 체크 함수 (상단 표시)
def show_location_connection_status():
    my_city = get_current_city()
    city_eng = city_map.get(my_city, my_city)
    url = f"{BASE_URL}?q={city_eng}&appid={API_KEY}&units=metric&lang=kr"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            st.success(f"✅ 내 위치({my_city}) 날씨 API 연결 성공!")
        elif response.status_code == 401:
            st.error("❌ 내 위치 API 키 오류: 올바르지 않거나 활성화되지 않았습니다.")
        elif response.status_code == 404:
            st.warning(f"⚠️ 내 위치({my_city})를 찾을 수 없습니다.")
        else:
            st.warning(f"⚠️ 내 위치 API 연결 상태: {response.status_code}")
    except Exception as e:
        st.error(f"❌ 내 위치 API 연결 실패: {e}")

check_api_connection()
# get_current_city 정의 이후에 호출
# ...existing code...
def get_location_by_ip():
    try:
        ip_api_url = "https://ipinfo.io/json"
        response = requests.get(ip_api_url)
        if response.status_code == 200:
            data = response.json()
            lat_lon = data.get('loc', '37.5665,126.9780')
            latitude, longitude = map(float, lat_lon.split(','))
            # OpenStreetMap Nominatim API로 역지오코딩
            try:
                nominatim_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}&zoom=10&addressdetails=1"
                nomi_resp = requests.get(nominatim_url, headers={"User-Agent": "weather-app"}, timeout=5)
                if nomi_resp.status_code == 200:
                    nomi_data = nomi_resp.json()
                    address = nomi_data.get('address', {})
                    # city, town, village, state 중 우선순위로 도시명 추출
                    city = address.get('city') or address.get('town') or address.get('village') or address.get('state') or '알수없음'
                else:
                    city = data.get('city', '서울')
            except Exception:
                city = data.get('city', '서울')
            return latitude, longitude, city
        else:
            st.error("IP 기반 위치 정보를 가져오는 데 실패했습니다.")
            return None, None, None
    except Exception as e:
        st.error(f"IP 기반 위치 정보를 가져오는 중 오류 발생: {e}")
        return None, None, None

def get_weather_data(lat, lon, units='metric', lang='kr'):
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'units': units,
        'lang': lang
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"OpenWeather API 호출에 실패했습니다. (상태 코드: {response.status_code})")
        return None

import json
with open('city_map.json', encoding='utf-8') as f:
    city_map = json.load(f)
korean_cities = list(city_map.keys())

# 공통 날씨/주간 카드 함수
def show_city_weather(city_name, location=False):
    city_eng = city_map.get(city_name, city_name)
    if city_name == "김포":
        lat, lon = 37.6153, 126.7159
        url = f"{BASE_URL}?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=kr"
    else:
        url = f"{BASE_URL}?q={city_eng}&appid={API_KEY}&units=metric&lang=kr"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_card(data, city_name, location=location)
        st.session_state.last_city_weather = data
        st.session_state.last_city_name = city_name
        return data
    else:
        st.error(f"[{city_name}] 날씨 정보를 가져올 수 없습니다. (상태 코드: {response.status_code})")
        return None

def show_weekly_weather(city_name, data=None):
    if data is None:
        data = show_city_weather(city_name)
    if data:
        lat, lon = data['coord']['lat'], data['coord']['lon']
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&lang=kr&appid={API_KEY}"
        resp_forecast = requests.get(forecast_url)
        if resp_forecast.status_code == 200:
            forecast_data = resp_forecast.json()
            forecast_list = forecast_data.get('list', [])
            if forecast_list:
                weekly_weather_card(forecast_list, city_name)
            else:
                st.warning("주간 예보 데이터가 없습니다.")
        else:
            st.warning("주간 날씨 정보를 가져올 수 없습니다.")

def get_current_city():
    try:
        res = requests.get("http://ip-api.com/json", timeout=5)
        if res.status_code == 200:
            info = res.json()
            city = info.get("city", "서울")
            for k, v in city_map.items():
                if v.lower() == city.lower():
                    return k
            return city
    except Exception:
        pass
    return "서울"

def weather_card(data, city_name, location=False):
    # 아이콘 코드와 이미지 파일명 매핑 객체
    # images 폴더 내 실제 파일명 기반 자동 매핑
    icon_map = {
        '01d': 'sunny.jpg',
        '01n': 'sunny.jpg',
        '02d': 'parrtly cloudy.jpg',
        '02n': 'parrtly cloudy.jpg',
        '03d': 'cloudy.jpg',
        '03n': 'cloudy.jpg',
        '04d': 'overcast.jpg',
        '04n': 'overcast.jpg',
        '09d': 'showers.jpg',
        '09n': 'showers.jpg',
        '10d': 'rain.jpg',
        '10n': 'rain.jpg',
        '11d': 'thunderstorm.jpg',
        '11n': 'thunderstorm.jpg',
        '13d': 'snow.jpg',
        '13n': 'snow.jpg',
        '50d': 'mist.jpg',
        '50n': 'mist.jpg',
    }
    icon_code = data['weather'][0]['icon']
    image_file = icon_map.get(icon_code, 'sunny.jpg')
    # 로컬 환경이면 images 폴더의 이미지 사용, 아니면 OpenWeather 아이콘 URL 사용
    local_image_path = os.path.join('images', image_file)
    if os.path.exists(local_image_path):
        image_path = local_image_path
    else:
        image_path = f"https://openweathermap.org/img/wn/{icon_code}@4x.png"
    card_height = 260
    # 미세먼지/체감온도 등 추가 정보
    feels_like = data['main'].get('feels_like', None)
    # 카드 디자인 개선: 그라데이션, 이미지 오버레이, 애니메이션 효과, 정보 배치 개선
    st.markdown(f"""
        <div style='position: relative; border-radius: 1.2rem; box-shadow: 0 4px 16px #0003; margin-bottom: 2rem; min-height: {card_height}px; height: {card_height}px; width: 100%; overflow: hidden; background: linear-gradient(120deg, #2b5876 0%, #4e4376 100%); display: flex; align-items: stretch;'>
            <div style='flex:2; padding:2.2rem 2rem; display:flex; flex-direction:column; justify-content:center; z-index:2;'>
                <h2 style='margin:0; color:#fff; text-shadow: 0 2px 8px #0006; font-size:clamp(1.2rem,3vw,2.2rem); font-family: "Pretendard", "Noto Sans KR", sans-serif;'>{city_name}{' <span style="font-size:1rem; color:#ffd700;">(내 위치)</span>' if location else ''}</h2>
                <h1 style='margin:0; font-size:clamp(2.2rem,6vw,3.7rem); color:#fff; text-shadow: 0 2px 8px #0006; font-family: "Pretendard", "Noto Sans KR", sans-serif;'>
                    <span style="display:inline-block; animation: tempPop 0.7s cubic-bezier(.68,-0.55,.27,1.55) 1;">{data['main']['temp']}°C</span>
                </h1>
                <p style='margin:0; font-size:clamp(1.1rem,3vw,1.6rem); color:#fff; text-shadow: 0 2px 8px #0006; font-family: "Pretendard", "Noto Sans KR", sans-serif;'>
                    {data['weather'][0]['description'].capitalize()}
                </p>
                <div style='margin-top:1.2rem; color:#fff; text-shadow: 0 2px 8px #0006; font-size:clamp(1rem,2vw,1.3rem); font-family: "Pretendard", "Noto Sans KR", sans-serif;'>
                    <span>습도: {data['main']['humidity']}%</span> | <span>풍속: {data['wind']['speed']} m/s</span>
                    {'| <span>체감온도: ' + str(feels_like) + '°C</span>' if feels_like is not None else ''}
                </div>
            </div>
            <div style='flex:1; position:relative; display:flex; align-items:center; justify-content:center; background:rgba(0,0,0,0.03);'>
                <img src='{image_path}' style='height:{card_height}px; width:100%; object-fit:cover; border-radius:0 1.2rem 1.2rem 0; box-shadow:0 2px 8px #0002; filter:brightness(0.98) drop-shadow(0 2px 8px #0002); z-index:1;'>
                <div style='position:absolute; top:10px; right:10px; z-index:2;'>
                    <span style="background:rgba(255,255,255,0.7); border-radius:0.7rem; padding:0.3rem 0.7rem; font-size:1.1rem; color:#333; font-family: 'Pretendard', 'Noto Sans KR', sans-serif; box-shadow:0 2px 8px #0001;">{data['weather'][0]['main']}</span>
                </div>
            </div>
        </div>
        <style>
        @keyframes tempPop {{
            0% {{ transform: scale(0.7); opacity:0; }}
            70% {{ transform: scale(1.15); opacity:1; }}
            100% {{ transform: scale(1); opacity:1; }}
        }}
        </style>
    """, unsafe_allow_html=True)

# 주간 날씨 카드
def weekly_weather_card(daily_list, city_name):
    st.markdown(f"<h3 style='margin-top:2rem;'>{city_name}의 주간 날씨 (테이블, 5일 3시간 간격 예보)</h3>", unsafe_allow_html=True)
    import datetime
    import pandas as pd
    # 요일 한글 변환
    weekday_kr = ['월', '화', '수', '목', '금', '토', '일']
    # 날짜별로 그룹화
    day_groups = {}
    for item in daily_list:
        dt = datetime.datetime.fromtimestamp(item['dt'])
        day_str = dt.strftime('%Y-%m-%d')
        if day_str not in day_groups:
            day_groups[day_str] = []
        day_groups[day_str].append(item)
    week_rows = []
    for day_str, items in list(day_groups.items())[:7]:
        # 대표값 추출: 최고/최저/평균 기온, 대표 날씨(가장 많이 등장한 description)
        temps = [it['main']['temp'] for it in items]
        humidities = [it['main']['humidity'] for it in items]
        winds = [it['wind']['speed'] for it in items]
        icons = [it['weather'][0]['icon'] for it in items]
        descs = [it['weather'][0]['description'] for it in items]
        # 대표 아이콘/날씨: 가장 많이 등장한 값
        from collections import Counter
        icon_code = Counter(icons).most_common(1)[0][0]
        desc = Counter(descs).most_common(1)[0][0]
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"
        # 요일 한글로 변환
        dt = datetime.datetime.strptime(day_str, '%Y-%m-%d')
        weekday_idx = dt.weekday()
        weekday_name = weekday_kr[weekday_idx]
        week_rows.append({
            '날짜': f"{day_str} ({weekday_name})",
            '아이콘': f"<img src='{icon_url}' style='width:32px; height:32px;'>",
            '최고기온(°C)': max(temps),
            '최저기온(°C)': min(temps),
            '평균기온(°C)': round(sum(temps)/len(temps),1),
            '날씨': desc,
            '평균습도(%)': round(sum(humidities)/len(humidities),1),
            '평균풍속(m/s)': round(sum(winds)/len(winds),1)
        })
    df = pd.DataFrame(week_rows)
    st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
 
st.markdown("<h1 style='text-align:center; color:#2b5876;'>🌤️ 날씨 웹앱</h1>", unsafe_allow_html=True)

import time
# 실시간 기상 레이더 지도 표시 버튼
with st.expander("실시간 기상 레이더 지도 보기", expanded=False):
    st.markdown("<b>정확한 GPS 위치를 사용하려면 브라우저 위치 권한을 허용하세요.</b>", unsafe_allow_html=True)
    radar_col1, radar_col2 = st.columns([1,1])
    with radar_col1:
        radar_gps_btn = st.button("내 위치 기반 레이더 지도 열기", key="radar_gps_btn")
    with radar_col2:
        radar_korea_btn = st.button("한국 중심 레이더 지도 열기", key="radar_korea_btn")
    if radar_gps_btn:
        coords = streamlit_js_eval(
            js_expressions="new Promise((resolve, reject) => {navigator.geolocation.getCurrentPosition((pos) => resolve({lat: pos.coords.latitude, lon: pos.coords.longitude}), (err) => resolve({error: err.message}) )})",
            key="get_gps"
        )
        time.sleep(0.5)
        if coords and "lat" in coords and "lon" in coords:
            show_weather_radar(center_lat=coords["lat"], center_lon=coords["lon"])
        elif coords and "error" in coords:
            st.error(f"브라우저 위치 권한 오류: {coords['error']}")
        else:
            st.error("브라우저 위치 권한을 허용해야 내 위치 기반 지도를 볼 수 있습니다.")
    elif radar_korea_btn:
        show_weather_radar()

# 3가지 선택 라디오
option = st.radio("날씨 조회 방법을 선택하세요", ["내 위치 기반", "도시 선택", "도시명 입력"], horizontal=True, key="main_radio")

if option == "내 위치 기반":
    st.markdown("<b>정확한 GPS 위치를 사용하려면 브라우저 위치 권한을 허용하세요.</b>", unsafe_allow_html=True)
    coords = streamlit_js_eval(
        js_expressions="new Promise((resolve, reject) => {navigator.geolocation.getCurrentPosition((pos) => resolve({lat: pos.coords.latitude, lon: pos.coords.longitude}), (err) => resolve({error: err.message}) )})",
        key="get_gps"
    )
    col_gps1, col_gps2 = st.columns([1,1])
    with col_gps1:
        gps_weather_clicked = st.button("내 위치 날씨 카드 보기", key="gps_weather_btn")
    with col_gps2:
        gps_weekly_clicked = st.button("내 위치 주간 날씨 테이블 보기", key="gps_weekly_btn")
    if gps_weather_clicked or gps_weekly_clicked:
        if coords and "lat" in coords and "lon" in coords:
            lat, lon = coords["lat"], coords["lon"]
            # 역지오코딩으로 도시명 추출
            try:
                nominatim_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
                nomi_resp = requests.get(nominatim_url, headers={"User-Agent": "weather-app"}, timeout=5)
                if nomi_resp.status_code == 200:
                    nomi_data = nomi_resp.json()
                    address = nomi_data.get('address', {})
                    my_city = address.get('city') or address.get('town') or address.get('village') or address.get('state') or '알수없음'
                else:
                    my_city = '알수없음'
            except Exception:
                my_city = '알수없음'
            st.session_state.weather_logs.append(f"[내 위치-GPS] city: {my_city}, lat: {lat}, lon: {lon}")
            if gps_weather_clicked:
                url = f"{BASE_URL}?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=kr"
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    weather_card(data, my_city, location=True)
                else:
                    st.session_state.weather_logs.append(f"[내 위치-GPS] 오류: 내 위치 기반 날씨 정보를 가져올 수 없습니다.")
                    st.error("내 위치 기반 날씨 정보를 가져올 수 없습니다.")
            if gps_weekly_clicked:
                forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&lang=kr&appid={API_KEY}"
                resp_forecast = requests.get(forecast_url)
                if resp_forecast.status_code == 200:
                    forecast_data = resp_forecast.json()
                    forecast_list = forecast_data.get('list', [])
                    if forecast_list:
                        weekly_weather_card(forecast_list, my_city)
                    else:
                        st.warning("주간 예보 데이터가 없습니다.")
                else:
                    st.warning("주간 날씨 정보를 가져올 수 없습니다.")
        elif coords and "error" in coords:
            st.session_state.weather_logs.append(f"[내 위치-GPS] 오류: {coords['error']}")
            st.error(f"브라우저 위치 권한 오류: {coords['error']}")
        else:
            st.session_state.weather_logs.append(f"[내 위치-GPS] 오류: 브라우저 위치 권한이 필요합니다.")
            st.error("브라우저 위치 권한을 허용해야 정확한 GPS 위치를 사용할 수 있습니다.")
elif option == "도시 선택":
    korea_cities = [
        "서울", "부산", "인천", "대구", "광주", "대전", "울산", "세종", "수원", "성남", "고양", "용인", "부천", "안산", "남양주", "화성", "평택", "의정부", "시흥", "파주", "김포", "광명", "광주(경기)", "군포", "오산", "이천", "안양", "구리", "안성", "포천", "하남", "양주", "여주", "동두천", "과천", "춘천", "원주", "강릉", "동해", "속초", "삼척", "태백", "홍천", "철원", "화천", "양구", "인제", "고성", "양양", "청주", "충주", "제천", "보은", "옥천", "영동", "증평", "진천", "괴산", "음성", "단양", "천안", "공주", "보령", "아산", "서산", "논산", "계룡", "당진", "금산", "부여", "서천", "청양", "홍성", "예산", "태안", "전주", "군산", "익산", "정읍", "남원", "김제", "완주", "진안", "무주", "장수", "임실", "순창", "고창", "부안", "목포", "여수", "순천", "나주", "광양", "담양", "곡성", "구례", "고흥", "보성", "화순", "장흥", "강진", "해남", "영암", "무안", "함평", "영광", "장성", "완도", "신안", "포항", "경주", "김천", "안동", "구미", "영주", "영천", "상주", "문경", "경산", "군위", "의성", "청송", "영양", "영덕", "청도", "고령", "성주", "칠곡", "예천", "봉화", "울진", "울릉", "창원", "진주", "통영", "사천", "김해", "밀양", "거제", "양산", "의령", "함안", "창녕", "고성(경남)", "남해", "하동", "산청", "함양", "거창", "합천", "제주", "서귀포"
    ]
    city_select = st.selectbox("도시를 선택하세요", korea_cities, index=korea_cities.index("서울") if "서울" in korea_cities else 0, key="city_select")
    city_map = {
        "서울": "Seoul", "부산": "Busan", "인천": "Incheon", "대구": "Daegu", "광주": "Gwangju", "대전": "Daejeon", "울산": "Ulsan", "세종": "Sejong",
        "수원": "Suwon", "성남": "Seongnam", "고양": "Goyang", "용인": "Yongin", "부천": "Bucheon", "안산": "Ansan", "남양주": "Namyangju", "화성": "Hwaseong",
        "평택": "Pyeongtaek", "의정부": "Uijeongbu", "시흥": "Siheung", "파주": "Paju", "김포": "Gimpo", "광명": "Gwangmyeong", "군포": "Gunpo", "오산": "Osan",
        "이천": "Icheon", "안양": "Anyang", "구리": "Guri", "안성": "Anseong", "포천": "Pocheon", "하남": "Hanam", "양주": "Yangju", "여주": "Yeoju",
        "동두천": "Dongducheon", "과천": "Gwacheon", "광주(경기)": "Gwangju", "춘천": "Chuncheon", "원주": "Wonju", "강릉": "Gangneung", "동해": "Donghae",
        "속초": "Sokcho", "삼척": "Samcheok", "태백": "Taebaek", "홍천": "Hongcheon", "철원": "Cheorwon", "화천": "Hwacheon", "양구": "Yanggu", "인제": "Inje",
        "고성": "Goseong", "양양": "Yangyang", "청주": "Cheongju", "충주": "Chungju", "제천": "Jecheon", "보은": "Boeun", "옥천": "Okcheon", "영동": "Yeongdong",
        "증평": "Jeungpyeong", "진천": "Jincheon", "괴산": "Goesan", "음성": "Eumseong", "단양": "Danyang", "천안": "Cheonan", "공주": "Gongju", "보령": "Boryeong",
        "아산": "Asan", "서산": "Seosan", "논산": "Nonsan", "계룡": "Gyeryong", "당진": "Dangjin", "금산": "Geumsan", "부여": "Buyeo", "서천": "Seocheon",
        "청양": "Cheongyang", "홍성": "Hongseong", "예산": "Yesan", "태안": "Taean", "전주": "Jeonju", "군산": "Gunsan", "익산": "Iksan", "정읍": "Jeongeup",
        "남원": "Namwon", "김제": "Gimje", "완주": "Wanju", "진안": "Jinan", "무주": "Muju", "장수": "Jangsu", "임실": "Imsil", "순창": "Sunchang",
        "고창": "Gochang", "부안": "Buan", "목포": "Mokpo", "여수": "Yeosu", "순천": "Suncheon", "나주": "Naju", "광양": "Gwangyang", "담양": "Damyang",
        "곡성": "Gokseong", "구례": "Gurye", "고흥": "Goheung", "보성": "Boseong", "화순": "Hwasun", "장흥": "Jangheung", "강진": "Gangjin", "해남": "Haenam",
        "영암": "Yeongam", "무안": "Muan", "함평": "Hampyeong", "영광": "Yeonggwang", "장성": "Jangseong", "완도": "Wando", "신안": "Shinan", "포항": "Pohang",
        "경주": "Gyeongju", "김천": "Gimcheon", "안동": "Andong", "구미": "Gumi", "영주": "Yeongju", "영천": "Yeongcheon", "상주": "Sangju", "문경": "Mungyeong",
        "경산": "Gyeongsan", "군위": "Gunwi", "의성": "Uiseong", "청송": "Cheongsong", "영양": "Yeongyang", "영덕": "Yeongdeok", "청도": "Cheongdo", "고령": "Goryeong",
        "성주": "Seongju", "칠곡": "Chilgok", "예천": "Yecheon", "봉화": "Bonghwa", "울진": "Uljin", "울릉": "Ulleung", "창원": "Changwon", "진주": "Jinju",
        "통영": "Tongyeong", "사천": "Sacheon", "김해": "Gimhae", "밀양": "Miryang", "거제": "Geoje", "양산": "Yangsan", "의령": "Uiryeong", "함안": "Haman",
        "창녕": "Changnyeong", "고성(경남)": "Goseong", "남해": "Namhae", "하동": "Hadong", "산청": "Sancheong", "함양": "Hamyang", "거창": "Geochang",
        "합천": "Hapcheon", "제주": "Jeju", "서귀포": "Seogwipo"
    }
    city_eng = city_map.get(city_select, city_select)
    if city_select == "김포":
        lat, lon = 37.6153, 126.7159
        url = f"{BASE_URL}?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=kr"
    else:
        url = f"{BASE_URL}?q={city_eng}&appid={API_KEY}&units=metric&lang=kr"
    col_city1, col_city2 = st.columns([1,1])
    with col_city1:
        city_weather_clicked = st.button('도시 날씨 카드 보기', key="city_weather_btn")
    with col_city2:
        city_weekly_clicked = st.button('주간 날씨 테이블 보기', key="city_weekly_btn")
    if city_weather_clicked or city_weekly_clicked:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather_card(data, city_select)
            st.session_state.last_city_weather = data
            st.session_state.last_city_name = city_select
            if city_weekly_clicked:
                lat, lon = data['coord']['lat'], data['coord']['lon']
                forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&lang=kr&appid={API_KEY}"
                resp_forecast = requests.get(forecast_url)
                if resp_forecast.status_code == 200:
                    forecast_data = resp_forecast.json()
                    forecast_list = forecast_data.get('list', [])
                    if forecast_list:
                        weekly_weather_card(forecast_list, city_select)
                    else:
                        st.warning("주간 예보 데이터가 없습니다.")
                else:
                    st.warning("주간 날씨 정보를 가져올 수 없습니다.")
        elif response.status_code == 401:
            st.session_state.weather_logs.append(f"[{city_select}] 오류: API 키가 올바르지 않거나 활성화되지 않았습니다. (401 Unauthorized)")
            st.error("오류: API 키가 올바르지 않거나 활성화되지 않았습니다. (401 Unauthorized)")
        elif response.status_code == 404:
            st.session_state.weather_logs.append(f"[{city_select}] 오류: 도시 이름을 찾을 수 없습니다.")
            st.error("오류: 도시 이름을 찾을 수 없습니다. 다시 입력해 주세요.")
        else:
            st.session_state.weather_logs.append(f"[{city_select}] 오류: API 호출 실패. 상태 코드: {response.status_code}")
            st.error(f"오류: API 호출 실패. 상태 코드: {response.status_code}")
elif option == "도시명 입력":
    city_input = st.text_input("도시명을 입력하세요 (한글/영문)", "", key="city_input")
    city_final = city_input.strip()
    city_map = {
        "서울": "Seoul", "부산": "Busan", "인천": "Incheon", "대구": "Daegu", "광주": "Gwangju", "대전": "Daejeon", "울산": "Ulsan", "세종": "Sejong",
        "수원": "Suwon", "성남": "Seongnam", "고양": "Goyang", "용인": "Yongin", "부천": "Bucheon", "안산": "Ansan", "남양주": "Namyangju", "화성": "Hwaseong",
        "평택": "Pyeongtaek", "의정부": "Uijeongbu", "시흥": "Siheung", "파주": "Paju", "김포": "Gimpo", "광명": "Gwangmyeong", "군포": "Gunpo", "오산": "Osan",
        "이천": "Icheon", "안양": "Anyang", "구리": "Guri", "안성": "Anseong", "포천": "Pocheon", "하남": "Hanam", "양주": "Yangju", "여주": "Yeoju",
        "동두천": "Dongducheon", "과천": "Gwacheon", "광주(경기)": "Gwangju", "춘천": "Chuncheon", "원주": "Wonju", "강릉": "Gangneung", "동해": "Donghae",
        "속초": "Sokcho", "삼척": "Samcheok", "태백": "Taebaek", "홍천": "Hongcheon", "철원": "Cheorwon", "화천": "Hwacheon", "양구": "Yanggu", "인제": "Inje",
        "고성": "Goseong", "양양": "Yangyang", "청주": "Cheongju", "충주": "Chungju", "제천": "Jecheon", "보은": "Boeun", "옥천": "Okcheon", "영동": "Yeongdong",
        "증평": "Jeungpyeong", "진천": "Jincheon", "괴산": "Goesan", "음성": "Eumseong", "단양": "Danyang", "천안": "Cheonan", "공주": "Gongju", "보령": "Boryeong",
        "아산": "Asan", "서산": "Seosan", "논산": "Nonsan", "계룡": "Gyeryong", "당진": "Dangjin", "금산": "Geumsan", "부여": "Buyeo", "서천": "Seocheon",
        "청양": "Cheongyang", "홍성": "Hongseong", "예산": "Yesan", "태안": "Taean", "전주": "Jeonju", "군산": "Gunsan", "익산": "Iksan", "정읍": "Jeongeup",
        "남원": "Namwon", "김제": "Gimje", "완주": "Wanju", "진안": "Jinan", "무주": "Muju", "장수": "Jangsu", "임실": "Imsil", "순창": "Sunchang",
        "고창": "Gochang", "부안": "Buan", "목포": "Mokpo", "여수": "Yeosu", "순천": "Suncheon", "나주": "Naju", "광양": "Gwangyang", "담양": "Damyang",
        "곡성": "Gokseong", "구례": "Gurye", "고흥": "Goheung", "보성": "Boseong", "화순": "Hwasun", "장흥": "Jangheung", "강진": "Gangjin", "해남": "Haenam",
        "영암": "Yeongam", "무안": "Muan", "함평": "Hampyeong", "영광": "Yeonggwang", "장성": "Jangseong", "완도": "Wando", "신안": "Shinan", "포항": "Pohang",
        "경주": "Gyeongju", "김천": "Gimcheon", "안동": "Andong", "구미": "Gumi", "영주": "Yeongju", "영천": "Yeongcheon", "상주": "Sangju", "문경": "Mungyeong",
        "경산": "Gyeongsan", "군위": "Gunwi", "의성": "Uiseong", "청송": "Cheongsong", "영양": "Yeongyang", "영덕": "Yeongdeok", "청도": "Cheongdo", "고령": "Goryeong",
        "성주": "Seongju", "칠곡": "Chilgok", "예천": "Yecheon", "봉화": "Bonghwa", "울진": "Uljin", "울릉": "Ulleung", "창원": "Changwon", "진주": "Jinju",
        "통영": "Tongyeong", "사천": "Sacheon", "김해": "Gimhae", "밀양": "Miryang", "거제": "Geoje", "양산": "Yangsan", "의령": "Uiryeong", "함안": "Haman",
        "창녕": "Changnyeong", "고성(경남)": "Goseong", "남해": "Namhae", "하동": "Hadong", "산청": "Sancheong", "함양": "Hamyang", "거창": "Geochang",
        "합천": "Hapcheon", "제주": "Jeju", "서귀포": "Seogwipo"
    }
    city_eng = city_map.get(city_final, city_final)
    if city_final == "김포":
        lat, lon = 37.6153, 126.7159
        url = f"{BASE_URL}?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=kr"
    else:
        url = f"{BASE_URL}?q={city_eng}&appid={API_KEY}&units=metric&lang=kr"
    col_input1, col_input2 = st.columns([1,1])
    with col_input1:
        input_weather_clicked = st.button('도시 날씨 카드 보기', key="input_weather_btn")
    with col_input2:
        input_weekly_clicked = st.button('주간 날씨 테이블 보기', key="input_weekly_btn")
    if input_weather_clicked or input_weekly_clicked:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather_card(data, city_final)
            st.session_state.last_city_weather = data
            st.session_state.last_city_name = city_final
            if input_weekly_clicked:
                lat, lon = data['coord']['lat'], data['coord']['lon']
                forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&lang=kr&appid={API_KEY}"
                resp_forecast = requests.get(forecast_url)
                if resp_forecast.status_code == 200:
                    forecast_data = resp_forecast.json()
                    forecast_list = forecast_data.get('list', [])
                    if forecast_list:
                        weekly_weather_card(forecast_list, city_final)
                    else:
                        st.warning("주간 예보 데이터가 없습니다.")
                else:
                    st.warning("주간 날씨 정보를 가져올 수 없습니다.")
        elif response.status_code == 401:
            st.session_state.weather_logs.append(f"[{city_final}] 오류: API 키가 올바르지 않거나 활성화되지 않았습니다. (401 Unauthorized)")
            st.error("오류: API 키가 올바르지 않거나 활성화되지 않았습니다. (401 Unauthorized)")
        elif response.status_code == 404:
            st.session_state.weather_logs.append(f"[{city_final}] 오류: 도시 이름을 찾을 수 없습니다.")
            st.error("오류: 도시 이름을 찾을 수 없습니다. 다시 입력해 주세요.")
        else:
            st.session_state.weather_logs.append(f"[{city_final}] 오류: API 호출 실패. 상태 코드: {response.status_code}")
            st.error(f"오류: API 호출 실패. 상태 코드: {response.status_code}")

# 항상 하단에 로그 창 표시 (중복 제거)
st.markdown("---")
with st.expander("날씨 요청/결과 로그 보기", expanded=True):
    for log in st.session_state.weather_logs[-20:]:
        st.write(log)

