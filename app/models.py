# app/models.py
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy import func


class Users(Base):
    """
    Model representing users in the application.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    auto_check_enabled = Column(Boolean, default=False)

    favorite_locations = relationship("FavoriteLocation", back_populates="owner")


class FavoriteLocation(Base):
    """
    Model representing a user's favorite locations.
    """

    __tablename__ = "favorite_locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    latitude = Column(String)
    longitude = Column(String)

    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("Users", back_populates="favorite_locations")


class WeatherData(Base):
    """
    Model representing weather data associated with locations.
    """

    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    temperature = Column(Float)
    humidity = Column(Float)
    weather_description = Column(String)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("Users")


class UserVerification(BaseModel):
    old_password: str
    password: str
    password2: str
