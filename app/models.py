# app/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy import func


class Users(Base):
    __tablename__ = "users"

    # Columns in the users table
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    favorite_locations = relationship("FavoriteLocation", back_populates="owner")


class FavoriteLocation(Base):
    __tablename__ = "favorite_locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    latitude = Column(String)
    longitude = Column(String)

    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("Users", back_populates="favorite_locations")


class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    temperature = Column(Float)
    humidity = Column(Float)
    weather_description = Column(String)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Foreign key for user if you want to associate weather data with users
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("Users")
