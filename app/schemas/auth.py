# app/schemas/auth.py
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

class UserResponse(BaseModel):
    id: Optional[str]  # Supabase user id
    email: EmailStr
    user_metadata: Optional[Dict[str, Any]] = None  # To store extra data like username

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str