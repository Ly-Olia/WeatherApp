from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse
from app import schemas, models, database, crud

from app.email_utils import send_email
from app.routers.auth import get_current_user
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

router = APIRouter(
    prefix="/weather", tags=["weather"], responses={404: {"description": "Not Found"}}
)

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse, name="main_page")
async def weather_main_page(request: Request, db: Session = Depends(database.get_db)):
    """
    Render the main weather page displaying favorite cities.
    """
    user = await get_current_user(request)

    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    favorite_cities = crud.get_favorite_locations(db, user_id=user.get("id"))

    return templates.TemplateResponse("main_page.html", {
        "request": request,
        "favorite_cities": favorite_cities,
        "user": user
    })


@router.get("/current_weather", response_class=HTMLResponse)
async def get_weather(request: Request, city: str,
                      user=Depends(get_current_user)):
    """
    Fetch and display the current weather for a given city.
    """
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    try:
        lat, lon = await crud.get_coordinates(city)
    except HTTPException as e:
        return RedirectResponse(url=f"/weather/?error={e.detail}", status_code=status.HTTP_302_FOUND)

    weather_data = await crud.get_current_weather(lat, lon)
    if weather_data is None:
        return RedirectResponse(url=f"/weather/?error=Weather data not found for '{city}'.",
                                status_code=status.HTTP_302_FOUND)

    forecast_data = await crud.get_5_day_forecast(lat, lon)

    # Call the function to check if it will rain today
    will_rain, total_rain_volume, rain_times = crud.will_it_rain_today(forecast_data)
    return templates.TemplateResponse("weather_details.html", {
        "request": request,
        "city": city,
        "weather": weather_data,
        "will_rain": will_rain,
        "rain_volume": total_rain_volume,
        "rain_times": rain_times,  # Pass rain times here
        "error": None
    })


@router.post("/favorite_city/", response_class=RedirectResponse)
async def add_favorite_city(city: schemas.FavoriteLocationBase, db: Session = Depends(database.get_db),
                            user=Depends(get_current_user)):
    """
    Add a city to the user's favorite locations.
    """
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    user_id = user.get("id")

    if crud.favorite_location_exists(db, user_id=user_id, city_name=city.name):
        error_message = "City already in favorites."
        return RedirectResponse(url=f"/weather/?error_favorite={error_message}", status_code=status.HTTP_302_FOUND)

    try:
        latitude, longitude = await crud.get_coordinates(city.name)
    except HTTPException:
        error_message = f"City not found: {city.name}"
        return RedirectResponse(url=f"/weather/?error_favorite={error_message}", status_code=status.HTTP_302_FOUND)

    crud.create_favorite_location(db=db, user_id=user_id, city_name=city.name,
                                  latitude=latitude, longitude=longitude)

    return RedirectResponse(url="/weather/", status_code=status.HTTP_302_FOUND)


@router.post("/favorite_city/{city_name}/delete", response_class=RedirectResponse)
def delete_favorite_city(city_name: str, db: Session = Depends(database.get_db), user=Depends(get_current_user)):
    """
    Deletes a city from the user's list of favorite locations.
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # Find the favorite city in the user's list
    favorite_location = db.query(models.FavoriteLocation).filter(
        models.FavoriteLocation.name == city_name,
        models.FavoriteLocation.owner_id == user.get("id")
    ).first()

    # If the city is not found, raise an error
    if not favorite_location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found in favorite locations")

    # Delete the city from the database
    db.delete(favorite_location)
    db.commit()

    # Redirect back to the main page after deletion
    return RedirectResponse(url="/weather", status_code=status.HTTP_302_FOUND)


@router.post("/send-welcome-email/")
def send_welcome_email(db: Session = Depends(database.get_db), user=Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    db_user = crud.get_user(db, user_id=user.get("id"))
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    subject = "Welcome to Our Service!"
    body = f"Hi {user.get("username")},\n\nWelcome to our service! We are glad to have you.\n\nBest Regards,\nThe Team"
    send_email(subject, body, db_user.email)
    return {"message": "Welcome email sent", "email": db_user.email}


@router.post("/send-current-weather/")
def send_current_weather(db: Session = Depends(database.get_db), user: models.Users = Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    db_user = crud.get_user(db, user_id=user.get("id"))
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch user's favorite locations
    favorite_locations = crud.get_favorite_locations(db, user_id=db_user.id)
    if not favorite_locations:
        raise HTTPException(status_code=404, detail="No favorite locations found for the user")

    # Fetch weather data for each favorite location
    weather_info = []
    for location in favorite_locations:
        weather_data = crud.fetch_weather_data(float(location.latitude), float(location.longitude))
        weather_info.append({
            "location": location.name,
            "weather": weather_data
        })

    # Compose the email body with weather information
    body = f"Hi {db_user.username},\n\nHere is the current weather for your favorite locations:\n\n"
    for info in weather_info:
        body += f"Location: {info['location']}\n"
        body += f"Weather: {info['weather']['description']}\n"
        body += f"Temperature: {info['weather']['temperature']}°C\n"
        body += f"Humidity: {info['weather']['humidity']}%\n\n"
    body += "Best Regards,\nThe Weather Assistant Team"

    # Send the email
    send_email("Your Favorite Locations' Weather Update", body, db_user.email)
    return {"message": "Weather email sent", "email": db_user.email}


@router.get("/rain-forecast/{city}")
async def get_rain_forecast(city: str):
    lat, lon = await crud.get_coordinates(city)
    forecast_data = await crud.get_5_day_forecast(lat, lon)

    if forecast_data:
        will_rain, total_rain_volume, rain_period = crud.will_it_rain_today(forecast_data)
        return {
            "city": city,
            "will_rain": will_rain,
            "rain_volume": total_rain_volume,
            "rain_period": rain_period,
            "weather": forecast_data
        }
    else:
        return {"error": "Failed to retrieve weather data."}


@router.post("/check-extreme-weather/")
async def check_and_send_alerts(city: str, db: Session = Depends(database.get_db)):
    lat, lon = await crud.get_coordinates(city)
    severe_weather = await crud.check_extreme_weather(lat, lon)
    # print(severe_weather.get("alerts"))
    user = crud.get_user(db, 6)
    weather_data = await crud.get_current_weather(lat, lon)
    if severe_weather.get('severe_weather'):
        # for alert in severe_weather.get("alerts", []):  # Iterate over the list
        # print(alert)
        await crud.send_severe_weather_alert(user, severe_weather.get("alerts"), city)
        return {"Message send": weather_data}
    else:

        return weather_data


@router.post("/check-severe-weather/")
async def check_and_send_alerts(db: Session = Depends(database.get_db)):
    users = crud.get_all_users(db)

    for user in users:
        favorite_locations = crud.get_favorite_locations(db, user_id=user.id)

        for location in favorite_locations:
            severe_weather = await crud.check_severe_weather(location.latitude, location.longitude)
            if severe_weather:
                await crud.send_severe_weather_alert(user, severe_weather)
