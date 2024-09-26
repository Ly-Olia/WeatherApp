# app/main.py

from fastapi import FastAPI

from app import database, models
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
async def root() -> RedirectResponse:
    """
    Redirect to the weather page.
    """
    return RedirectResponse(url="/weather", status_code=status.HTTP_302_FOUND)
