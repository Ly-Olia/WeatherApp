from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse
from app import schemas, models, database, crud, utils

from app.email_utils import check_alerts
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
    db_user = crud.get_user(db, user.get("id"))

    return templates.TemplateResponse("main_page.html", {
        "request": request,
        "favorite_cities": favorite_cities,
        "user": db_user
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
        lat, lon = await utils.get_coordinates(city)
    except HTTPException as e:
        return RedirectResponse(url=f"/weather/?error={e.detail}", status_code=status.HTTP_302_FOUND)

    weather_data = await utils.get_current_weather(lat, lon)
    if weather_data is None:
        return RedirectResponse(url=f"/weather/?error=Weather data not found for '{city}'.",
                                status_code=status.HTTP_302_FOUND)

    forecast_data = await utils.get_5_day_forecast(lat, lon)

    # Call the function to check if it will rain today
    will_rain, total_rain_volume, rain_times = utils.will_it_rain_today(forecast_data)
    return templates.TemplateResponse("weather_details.html", {
        "request": request,
        "city": city,
        "weather": weather_data,
        "will_rain": will_rain,
        "rain_volume": total_rain_volume,
        "rain_times": rain_times,
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
        latitude, longitude = await utils.get_coordinates(city.name)
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


@router.get("/rain-forecast/{city}")
async def get_rain_forecast(city: str):
    """
    Get rain forecast for the specified city.
    """
    lat, lon = await utils.get_coordinates(city)
    forecast_data = await utils.get_5_day_forecast(lat, lon)

    if forecast_data:
        will_rain, total_rain_volume, rain_period = utils.will_it_rain_today(forecast_data)
        return {
            "city": city,
            "will_rain": will_rain,
            "rain_volume": total_rain_volume,
            "rain_period": rain_period,
            "weather": forecast_data
        }
    else:
        return {"error": "Failed to retrieve weather data."}


@router.post("/send-severe-weather-alert/")
async def check_and_send_alerts(
        request: Request,
        city: str = Form(...),
        db: Session = Depends(database.get_db)
):
    """
    Check for severe weather in the user's favorite cities and send an alert via email.
    """
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=302)

    lat, lon = await utils.get_coordinates(city)
    severe_weather = await utils.check_extreme_weather(lat, lon)

    if severe_weather.get('severe_weather'):
        alerts = severe_weather.get("alerts")
        alert_message = "\n".join(alerts)

        subject = f"Severe Weather Alert for {city}!"
        body = (
            f"Dear {user['username']},\n\n"
            f"Severe weather conditions are expected in {city}.\n"
            f"Details:\n{alert_message}\n\n"
            f"Please stay safe and take precautions.\n\n"
            f"Best regards,\nThe Weather App Team"
        )
        # Send the email
        check_alerts(user.get('id'), db, subject, body)

        return {"message": f"Severe weather alert sent to {user.get('username')}"}

    return {"message": "No severe weather detected."}


@router.post("/toggle-auto-check")
async def toggle_auto_check(
        db: Session = Depends(database.get_db),
        current_user: models.Users = Depends(get_current_user)
):
    """
    Toggle the auto_check_enabled flag for the current user.
    """
    try:
        user = current_user
        user = crud.get_user(db, user.get('id'))
        user.auto_check_enabled = not user.auto_check_enabled
        db.add(user)
        db.commit()
        db.refresh(user)
        return RedirectResponse(url="/weather/", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling auto-check: {str(e)}")


@router.post("/favorite_city/{city_id}/toggle_alert")
def toggle_send_alert(city_id: int, db: Session = Depends(database.get_db),
                      current_user: models.Users = Depends(get_current_user)):
    """
    Toggle the alert flag for a favorite city.
    """
    # Get the favorite location by ID and ensure it belongs to the current user
    favorite_location = db.query(models.FavoriteLocation).filter(
        models.FavoriteLocation.id == city_id,
        models.FavoriteLocation.owner_id == current_user.get('id')
    ).first()

    if not favorite_location:
        raise HTTPException(status_code=404, detail="Favorite city not found")

    # Toggle the send_alert value
    favorite_location.send_alert = not favorite_location.send_alert
    db.commit()

    return RedirectResponse(url="/weather/", status_code=status.HTTP_302_FOUND)
