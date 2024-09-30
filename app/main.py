from fastapi import FastAPI
from app import database, models, email_utils
from app.routers import users, weather, auth
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

# Create the database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Include routers for users, weather, and authentication
app.include_router(users.router)
app.include_router(weather.router)
app.include_router(auth.router)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize the background scheduler
scheduler = BackgroundScheduler()

@app.get("/")
async def root() -> RedirectResponse:
    """Redirect to the weather page."""
    return RedirectResponse(url="/weather", status_code=status.HTTP_302_FOUND)

# Schedule the job to check weather alerts every 3 minutes
@scheduler.scheduled_job('interval', minutes=2)
def scheduled_check_all_users_weather_alerts():
    loop = asyncio.new_event_loop()  # Create a new event loop
    asyncio.set_event_loop(loop)  # Set the new event loop as the current one
    with database.SessionLocal() as db:  # Create a new database session
        loop.run_until_complete(email_utils.check_all_users_weather_alerts(db))  # Run the async function
    loop.close()  # Close the loop after execution

# Start the scheduler
scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    """Shut down the scheduler on application shutdown."""
    scheduler.shutdown()
