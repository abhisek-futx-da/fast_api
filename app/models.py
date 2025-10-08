from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from .database import Base


# User model
class User(Base):
    __tablename__ = "users"

    # Initial columns
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # These columns were added in the second migration
    phone_number = Column(String, nullable=True)
    address = Column(String, nullable=True)


"""
Defines the database table structure using SQLAlchemy's ORM
[database tables as Python classes]
"""
