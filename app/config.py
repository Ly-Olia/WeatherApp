from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_KEY: str = '9a45e7fdc17743bdf127c34afe38cbeb'
    DATABASE_URL: str = 'postgresql://postgres:admin@localhost/WeatherAssistant'
    SECRET_KEY: str = 'KlgH6AzYDeZeGwD288to79I3vTHT8wp7'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    EMAIL_FROM: str = 'weather.app.fastapi@gmail.com'
    SMTP_SERVER: str = 'smtp.gmail.com'
    SMTP_PORT: int = 587
    SMTP_USER: str = 'weather.app.fastapi@gmail.com'
    SMTP_PASSWORD: str = 'vkgf nias njfv hvwj'


settings = Settings()
