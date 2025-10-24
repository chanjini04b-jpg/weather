import requests

def check_weather_api(city, api_key):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "kr"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        print("Status Code:", response.status_code)
        print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

if __name__ == "__main__":
    check_weather_api("Seoul", "4fc3dde824c23bc206029df5c0eba3a8")
