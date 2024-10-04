from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


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
    auto_check_enabled = Column(Boolean, default=False, nullable=False)

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
    send_alert = Column(Boolean, default=False, nullable=False)

    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("Users", back_populates="favorite_locations")
