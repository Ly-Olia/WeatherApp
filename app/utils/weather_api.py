import requests
from config import settings

def get_weather_by_coordinates(lat: float, lon: float, units: str = "metric", lang: str = "en"):
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={settings.API_KEY}&units={units}&lang={lang}'
    response = requests.get(url)
    return response.json()

def get_weather_by_city(city: str, country: str, units: str = "metric", lang: str = "en"):
    geo_url = f'http://api.openweathermap.org/geo/1.0/direct?q={city},{country}&limit=1&appid={settings.API_KEY}'
    geo_response = requests.get(geo_url).json()
    if not geo_response:
        return None
    lat = geo_response[0]['lat']
    lon = geo_response[0]['lon']
    return get_weather_by_coordinates(lat, lon, units, lang)
