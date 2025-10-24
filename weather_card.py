import streamlit as st
import os

def weather_card(data, city_name, location=False):
    icon_map = {
        '01d': 'sunny.jpg', '01n': 'sunny.jpg', '02d': 'parrtly cloudy.jpg', '02n': 'parrtly cloudy.jpg',
        '03d': 'cloudy.jpg', '03n': 'cloudy.jpg', '04d': 'overcast.jpg', '04n': 'overcast.jpg',
        '09d': 'showers.jpg', '09n': 'showers.jpg', '10d': 'rain.jpg', '10n': 'rain.jpg',
        '11d': 'thunderstorm.jpg', '11n': 'thunderstorm.jpg', '13d': 'snow.jpg', '13n': 'snow.jpg',
        '50d': 'mist.jpg', '50n': 'mist.jpg',
    }
    icon_code = data['weather'][0]['icon']
    image_file = icon_map.get(icon_code, 'sunny.jpg')
    local_image_path = os.path.join('images', image_file)
    if os.path.exists(local_image_path):
        image_path = local_image_path
    else:
        image_path = f"https://openweathermap.org/img/wn/{icon_code}@4x.png"
    card_height = 260
    feels_like = data['main'].get('feels_like', None)
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
