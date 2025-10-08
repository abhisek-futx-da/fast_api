from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# Shared properties for a user
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    address: Optional[str] = None


# Properties to receive via API on user creation
class UserCreate(UserBase):
    pass


# Properties to return to the client
class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
