from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    role: Optional[str] = "user"
    admin: Optional[dict] = None


class TokenData(BaseModel):
    email: Optional[str] = None
