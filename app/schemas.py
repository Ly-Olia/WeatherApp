from pydantic import BaseModel
from typing import Optional

class WeatherDataBase(BaseModel):
    city: str
    temperature: float
    condition: str

class WeatherDataCreate(WeatherDataBase):
    pass


class WeatherData(BaseModel):
    city: str
    temperature: float
    condition: str
    latitude: float
    longitude: float
    humidity: int
    weather_description: str
    wind_speed: float


    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str

class UserCreate(UserBase):
    hashed_password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Login(BaseModel):
    email: str
    password: str

class FavoriteLocationBase(BaseModel):
    name: str

class FavoriteLocationCreate(FavoriteLocationBase):
    pass

class FavoriteLocation(FavoriteLocationBase):
    id: int
    owner_id: int
    latitude: str
    longitude: str

    class Config:
        from_attributes = True
