from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
import re

class UserBase(BaseModel):
    login: str
    email: str

class UserCreate(UserBase):
    password: str

class UserAuthenticate(BaseModel):
    login: str
    password: str

class UserUpdate(BaseModel):
    login: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[date] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None

class User(UserBase):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[date] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


    class Config:
        orm_mode = True