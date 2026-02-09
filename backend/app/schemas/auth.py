"""Auth schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class RegisterRequest(BaseModel):
    """Schema for user registration."""
    email: str
    password: str
    name: str


class LoginRequest(BaseModel):
    """Schema for user login."""
    email: str
    password: str


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    email: str
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    """Schema for auth response with token."""
    user: UserResponse
    access_token: str
