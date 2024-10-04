import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from typing import Generator

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = sqlalchemy.orm.declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Get a database session to interact with the database.

    This is a generator function that yields a new database session.
    The session is properly closed after use to ensure that resources are released.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
