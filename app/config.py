from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    API_KEY: str  # API key for external service
    DATABASE_URL: str  # Database connection URL
    SECRET_KEY: str  # Secret key for cryptographic operations
    ALGORITHM: str  # Algorithm used for JWT token encoding
    ACCESS_TOKEN_EXPIRE_MINUTES: int  # Token expiration time in minutes
    EMAIL_FROM: str  # Sender email address for notifications
    SMTP_SERVER: str  # SMTP server address for sending emails
    SMTP_PORT: int  # Port number for the SMTP server
    SMTP_USER: str  # Username for SMTP authentication
    SMTP_PASSWORD: str  # Password for SMTP authentication

    class Config:
        env_file = ".env.py"  # Specify the .env file


# Create an instance of Settings
settings = Settings()
