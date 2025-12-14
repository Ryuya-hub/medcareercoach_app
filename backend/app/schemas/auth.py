from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str
    user_id: str
    role: str  # 'super_admin', 'coach', or 'client'


class TokenData(BaseModel):
    user_id: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    user_type: str  # 'coach' or 'client'
    name: str
    furigana: Optional[str] = None
    phone: Optional[str] = None


class ClientRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    furigana: Optional[str] = None
    phone: Optional[str] = None


class CoachRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    furigana: Optional[str] = None
    phone: Optional[str] = None
    invitation_code: str
