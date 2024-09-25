import asyncio
from fastapi import FastAPI

from app import database, models
from app.config import settings
from app.crud import get_5_day_forecast, will_it_rain_today, get_coordinates
from app.routers import users, weather, auth
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status
models.Base.metadata.create_all(bind=database.engine)


app = FastAPI()

# Dependency to get the database session
app.include_router(users.router)
app.include_router(weather.router)
app.include_router(auth.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return RedirectResponse(url="/weather", status_code=status.HTTP_302_FOUND)


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
