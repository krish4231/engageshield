"""Auth schemas for request/response validation."""

from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime


class UserRegister(BaseModel):
    email: str
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}
