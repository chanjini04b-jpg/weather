import streamlit as st
import pandas as pd
import datetime
from collections import Counter

def weekly_weather_card(daily_list, city_name):
    st.markdown(f"<h3 style='margin-top:2rem;'>{city_name}의 주간 날씨 (테이블, 5일 3시간 간격 예보)</h3>", unsafe_allow_html=True)
    weekday_kr = ['월', '화', '수', '목', '금', '토', '일']
    day_groups = {}
    for item in daily_list:
        dt = datetime.datetime.fromtimestamp(item['dt'])
        day_str = dt.strftime('%Y-%m-%d')
        if day_str not in day_groups:
            day_groups[day_str] = []
        day_groups[day_str].append(item)
    week_rows = []
    for day_str, items in list(day_groups.items())[:7]:
        temps = [it['main']['temp'] for it in items]
        humidities = [it['main']['humidity'] for it in items]
        winds = [it['wind']['speed'] for it in items]
        icons = [it['weather'][0]['icon'] for it in items]
        descs = [it['weather'][0]['description'] for it in items]
        icon_code = Counter(icons).most_common(1)[0][0]
        desc = Counter(descs).most_common(1)[0][0]
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"
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
