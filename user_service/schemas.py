from pydantic import BaseModel, field_validator
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

    @field_validator("phone_number")
    def validate_phone_number(cls, value):
        if not re.match(r'^\+\d{1,15}$', value):
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 1 до 15 цифр')
        return value
    
    @field_validator("date_of_birth")
    def validate_date_of_birth(cls, value):
        if value and value >= datetime.now().date():
            raise ValueError('Дата рождения должна быть в прошлом')
        return value

class User(UserBase):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[date] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator("phone_number")
    def validate_phone_number(cls, value):
        if not re.match(r'^\+\d{1,15}$', value):
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 1 до 15 цифр')
        return value
    
    @field_validator("date_of_birth")
    def validate_date_of_birth(cls, value):
        if value and value >= datetime.now().date():
            raise ValueError('Дата рождения должна быть в прошлом')
        return value

    class Config:
        orm_mode = True