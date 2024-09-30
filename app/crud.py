from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict, Union, Type

import httpx
import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models, schemas, email_utils
from .config import settings


def get_weather_data(db: Session, city: str, country: str) -> Optional[models.WeatherData]:
    return db.query(models.WeatherData).filter(models.WeatherData.city == city,
                                               models.WeatherData.country == country).first()


def create_weather_data(db: Session, weather_data: schemas.WeatherDataCreate) -> models.WeatherData:
    db_weather_data = models.WeatherData(**weather_data.model_dump())
    db.add(db_weather_data)
    db.commit()
    db.refresh(db_weather_data)
    return db_weather_data


def get_user(db: Session, user_id: int) -> Optional[models.Users]:
    """
    Retrieve a user by their ID from the database.
    """
    return db.query(models.Users).filter(models.Users.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.Users]:
    """
    Retrieve a user by their email from the database.
    """
    return db.query(models.Users).filter(models.Users.email == email).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.Users:
    """
    Create and store a new user in the database.
    """
    db_user = models.Users(
        email=user.email,
        username=user.username,
        hashed_password=user.hashed_password,
        first_name=user.first_name,
        last_name=user.last_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_users(db: Session) -> list[Type[models.Users]]:
    """
    Retrieve a list of all users from the database.
    """
    return db.query(models.Users).all()


def get_favorite_locations(db: Session, user_id: int) -> list[Type[models.FavoriteLocation]]:
    """
    Retrieve a list of favorite locations for a given user.
    """
    return db.query(models.FavoriteLocation).filter(models.FavoriteLocation.owner_id == user_id).all()


async def get_coordinates(city: str, state: Optional[str] = None, country: Optional[str] = None) -> Tuple[float, float]:
    """
    Fetch the geographic coordinates (latitude and longitude) of a city.
    """
    geocode_params = {
        "q": f"{city},{state},{country}" if state and country else city,
        "limit": 1,
        "appid": settings.API_KEY
    }

    async with httpx.AsyncClient() as client:
        response = await client.get("http://api.openweathermap.org/geo/1.0/direct", params=geocode_params)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch coordinates.")

    geocode_data = response.json()
    if not geocode_data or len(geocode_data) == 0:
        raise HTTPException(status_code=404, detail="City not found.")
    if 'lat' not in geocode_data[0] or 'lon' not in geocode_data[0]:
        raise HTTPException(status_code=500, detail="Incomplete geocode data returned by the API.")

    # Return the latitude and longitude
    return geocode_data[0]['lat'], geocode_data[0]['lon']


async def get_current_weather(lat: float, lon: float) -> schemas.WeatherData:
    """
    Fetch the current weather data for the given latitude and longitude.
    """
    current_weather_url = (
        f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={settings.API_KEY}&units=metric"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(current_weather_url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch current weather data.")

    weather_data = response.json()
    if "main" not in weather_data:
        raise HTTPException(status_code=500, detail="Error fetching weather data")

    weather = schemas.WeatherData(
        city=weather_data["name"],
        temperature=weather_data["main"]["temp"],
        condition=weather_data["weather"][0]["main"],
        wind_speed=weather_data["wind"]["speed"],
        latitude=lat,
        longitude=lon,
        humidity=weather_data["main"]["humidity"],
        weather_description=weather_data["weather"][0]["description"]
    )

    return weather


def create_favorite_location(db: Session, user_id: int, city_name: str, latitude: float,
                             longitude: float) -> models.FavoriteLocation:
    """
    Create and store a favorite location for a user in the database.
    """
    db_location = models.FavoriteLocation(
        name=city_name,
        latitude=str(latitude),
        longitude=str(longitude),
        owner_id=user_id
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def favorite_location_exists(db: Session, user_id: int, city_name: str) -> bool:
    """
    Check if a favorite location exists for a user.
    """
    return db.query(models.FavoriteLocation).filter(
        models.FavoriteLocation.owner_id == user_id,
        models.FavoriteLocation.name == city_name
    ).first() is not None


def fetch_weather_data(lat: float, lon: float) -> Dict[str, Union[float, int, str]]:
    """
    Fetch weather data from OpenWeatherMap API.
    """
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": settings.API_KEY,
        "units": "metric"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "pressure": data["main"]["pressure"],
            "visibility": data.get("visibility"),
            "rain": data.get("rain", {}).get("1h", 0),  # Rainfall in the last hour
            "cloud_coverage": data["clouds"]["all"],  # Cloud coverage percentage
            "sunrise": data["sys"].get("sunrise"),
            "sunset": data["sys"].get("sunset")
        }
    else:
        raise Exception(f"Error fetching weather data: {response.status_code}")


async def get_5_day_forecast(lat: float, lon: float, units: str = "metric") -> Dict:
    """
    Fetch a 5-day weather forecast for the given latitude and longitude.
    """
    forecast_params = {
        "lat": lat,
        "lon": lon,
        "appid": settings.API_KEY,
        "units": units
    }

    async with httpx.AsyncClient() as client:
        response = await client.get("http://api.openweathermap.org/data/2.5/forecast", params=forecast_params)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch weather data.")

    return response.json()


def categorize_time(dt: datetime) -> str:
    """
    Categorize the time into morning, afternoon, evening, or night.
    """
    hour = dt.hour
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon"
    elif 18 <= hour < 21:
        return "evening"
    else:
        return "night"


def will_it_rain_today(forecast_data: Dict) -> Tuple[bool, float, List[str]]:
    """
    Determine if it will rain today based on the forecast data.
    """
    current_date = datetime.now().date()
    rain_today = False
    total_rain_volume = 0.0

    rain_periods = []  # Store raw rain periods as tuples of (start_time, end_time)

    for entry in forecast_data["list"]:
        forecast_time = datetime.fromtimestamp(entry["dt"])
        if forecast_time.date() == current_date:
            weather_conditions = entry["weather"]
            for condition in weather_conditions:
                if "rain" in condition["description"].lower():
                    rain_today = True
                    rain_start_time = forecast_time
                    rain_end_time = forecast_time + timedelta(hours=3)

                    # Update total rain volume
                    total_rain_volume += entry["rain"].get("3h", 0.0)

                    # Append the rain period
                    rain_periods.append((rain_start_time, rain_end_time))
                    break

    # Combine overlapping rain periods
    combined_rain_periods = []
    if rain_periods:
        # Sort by start time
        rain_periods.sort(key=lambda x: x[0])

        # Initialize the first period
        current_start, current_end = rain_periods[0]

        for start, end in rain_periods[1:]:
            if start <= current_end:  # Overlapping or contiguous
                current_end = max(current_end, end)  # Extend the end time if necessary
            else:
                combined_rain_periods.append((current_start, current_end))
                current_start, current_end = start, end

        # Add the last period
        combined_rain_periods.append((current_start, current_end))

    # Format combined rain periods for display
    formatted_rain_periods = []
    for start, end in combined_rain_periods:
        formatted_rain_periods.append(f"{start.strftime('%I:%M %p')} ({categorize_time(start)}) - "
                                      f"{end.strftime('%I:%M %p')} ({categorize_time(end)})")

    total_rain_volume = round(total_rain_volume, 1)  # Round rain volume to 1 decimal
    return rain_today, total_rain_volume, formatted_rain_periods


async def send_severe_weather_alert(user: models.Users, alert, city):
    """
    Send an email alert about severe weather conditions.
    """

    alert_str = "\n".join(alert)
    message = (
        f"Severe weather conditions are expected in {city}.\n\n"
        f"Details: {alert_str}\n"
        f"\nBest Regards,\nThe Weather App Team"
    )
    subject = f"Severe Weather Alert in {city}!"
    email_utils.send_email(subject, message, user.email)


async def check_extreme_weather(lat: float, lon: float) -> dict:
    """
    Check for extreme weather conditions and return alerts if any.
    """
    weather_data = await get_current_weather(lat, lon)

    severe_conditions = {
        "Thunderstorm": "Thunderstorm conditions are present.",
        "Heavy Rain": "Heavy rain is expected.",
        "Snow": "Snowstorm conditions are present.",
        "Blizzard": "Blizzard conditions are present.",
        "Extreme Temperature": "Extreme temperatures detected.",
        "High Wind": "High wind speeds detected.",
        "Hail": "Hailstorm conditions are present.",
        "Fog": "Dense fog conditions are present.",
    }

    alerts = []
    for condition in severe_conditions:
        if condition.lower() in weather_data.condition.lower() or condition.lower() in weather_data.weather_description.lower():
            alerts.append(severe_conditions[weather_data.condition])

        # Check for extreme temperature
    if weather_data.temperature > 0 or weather_data.temperature < -10:
        alerts.append(severe_conditions["Extreme Temperature"])

        # Check for high wind speeds
    if weather_data.wind_speed > 50:
        alerts.append(severe_conditions["High Wind"])

    if alerts:
        return {
            "severe_weather": True,
            "weather_data": weather_data,
            "alerts": alerts,
        }
    else:
        return {
            "severe_weather": False,
            "alerts": [],
        }
