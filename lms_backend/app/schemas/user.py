from pydantic import BaseModel
from typing import Optional
from app.models.enums import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str
    role: UserRole

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    # Add other fields like phone number if added to User model
    phone_number: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool = True

    class Config:
        from_attributes = True

