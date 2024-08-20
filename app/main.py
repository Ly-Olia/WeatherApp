from datetime import datetime
from typing import List
import asyncio
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app import database, models
from app.config import settings
from app.crud import get_favorite_locations, fetch_weather_data, get_user, get_5_day_forecast, will_it_rain_today, \
    get_coordinates
from app.email_utils import send_email
from app.routers import users, weather, auth
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status
models.Base.metadata.create_all(bind=database.engine)

from app.database import SessionLocal, engine
from app.models import WeatherData

app = FastAPI()

# Dependency to get the database session
app.include_router(users.router)
app.include_router(weather.router)
app.include_router(auth.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return RedirectResponse(url="/weather", status_code=status.HTTP_302_FOUND)



# def main():
# db = SessionLocal()
# try:
#     user_id = 6  # User ID for which we are sending the weather updates
#     db_user = get_user(db, user_id=user_id)
#     favorite_locations = get_favorite_locations(db, user_id)
#
#     if not favorite_locations:
#         raise Exception(f"No favorite locations found for user ID {user_id}")
#
#     weather_info = []
#     for location in favorite_locations:
#         weather_data = fetch_weather_data(float(location.latitude), float(location.longitude))
#         weather_info.append({
#             "location": location.name,
#             "weather": weather_data
#         })
#
#     # Compose the email body with weather information
#     body = f"Hi {db_user.username},\n\nHere is the current weather for your favorite locations:\n\n"
#     for info in weather_info:
#         body += f"Location: {info['location']}\n"
#         body += f"Weather: {info['weather']['description']}\n"
#         body += f"Temperature: {info['weather']['temperature']}°C\n"
#         body += f"Humidity: {info['weather']['humidity']}%\n\n"
#     body += "Best Regards,\nThe Weather Assistant Team"
#     subject = f"Weather Update for - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
#     # Send the email
#     send_email(subject, body, db_user.email)
#
#     print(f"Weather email sent successfully for {db_user.email} at {datetime.now()}")
# except Exception as e:
#     print(f"Failed to send weather email: {e}")
# finally:
#     db.close()

async def main():
    lat, lon = await get_coordinates("Eindhoven")  # Longitude for Eindhoven
    api_key = settings.API_KEY
    forecast_data = await get_5_day_forecast(lat, lon, api_key)
    print(forecast_data)
    # print(forecast_data)
    if forecast_data:
        will_rain, total_rain_volume, rain_times = will_it_rain_today(forecast_data)
        if will_rain:
            print("It will rain today.", total_rain_volume, "mm ", rain_times)
        else:
            print("No rain expected today.", total_rain_volume, "mm", rain_times)
    else:
        print("Failed to retrieve weather data.")


if __name__ == "__main__":
    asyncio.run(main())
