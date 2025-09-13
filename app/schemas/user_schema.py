from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None  # Supabase can store it in user metadata


class UserOut(BaseModel):
    id: str  # Supabase user IDs are UUID strings
    email: EmailStr
    username: Optional[str] = None

    class Config:
        orm_mode = True
        