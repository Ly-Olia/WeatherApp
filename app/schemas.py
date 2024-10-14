from pydantic import BaseModel


class WeatherDataBase(BaseModel):
    city: str
    temperature: float
    condition: str


class WeatherDataCreate(WeatherDataBase):
    ...


class WeatherData(BaseModel):
    city: str
    temperature: float
    condition: str
    latitude: float
    longitude: float
    humidity: int
    weather_description: str
    wind_speed: float


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


class Login(BaseModel):
    email: str
    password: str


class FavoriteLocationBase(BaseModel):
    name: str


class FavoriteLocationCreate(FavoriteLocationBase):
    ...


class FavoriteLocation(FavoriteLocationBase):
    id: int
    owner_id: int
    latitude: str
    longitude: str
    name: str


class UserVerification(BaseModel):
    old_password: str
    password: str
    password2: str
