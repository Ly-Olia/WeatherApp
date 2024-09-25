from .. import models
from ..database import engine, get_db
from .auth import get_current_user, get_password_hash, verify_password

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not Found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


@router.get("/change-password", response_class=HTMLResponse)
async def edit_user_view(request: Request):
    """
    Render the change password page for the current user.
    """
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("change-password.html", {"request": request, "user": user})


@router.post("/change-password", response_class=HTMLResponse)
async def user_password_change(request: Request, old_password: str = Form(...),
                               password: str = Form(...),
                               password2: str = Form(...), db: Session = Depends(get_db)):
    """
        Change the user's password if the old password is verified.
    """
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    user_data = db.query(models.Users).filter(models.Users.id == user.get("id")).first()
    msg = "Invalid password"
    if user_data is not None:
        if password == password2 and verify_password(old_password, user_data.hashed_password):
            user_data.hashed_password = get_password_hash(password)
            db.add(user_data)
            db.commit()
            msg = 'Password updated'

    return templates.TemplateResponse("change-password.html", {"request": request, "user": user, "msg": msg})
