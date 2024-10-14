from typing import Optional, Type
from sqlalchemy.orm import Session
from . import models, schemas


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


def get_users_with_auto_check_enabled(db: Session) -> list[Type[models.Users]]:
    """
    Retrieve all users with auto-check enabled.
    """
    return db.query(models.Users).filter(models.Users.auto_check_enabled == True).all()


def get_favorite_locations(db: Session, user_id: int, send_alert: bool = None) -> list[Type[models.FavoriteLocation]]:
    """
    Retrieve a list of favorite locations for a given user, optionally filtering by send_alert.
    """
    query = db.query(models.FavoriteLocation).filter(models.FavoriteLocation.owner_id == user_id)
    if send_alert is not None:
        query = query.filter(models.FavoriteLocation.send_alert == send_alert)
    return query.all()






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
