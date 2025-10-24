import streamlit as st

def show_title():
    st.markdown("<h1 style='text-align:center; color:#2b5876;'>🌤️ 날씨 웹앱</h1>", unsafe_allow_html=True)

def show_log_window():
    st.markdown("---")
    if 'weather_logs' not in st.session_state:
        st.session_state.weather_logs = []
    with st.expander("날씨 요청/결과 로그 보기", expanded=True):
        for log in st.session_state.weather_logs[-20:]:
            st.write(log)
