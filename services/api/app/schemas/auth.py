from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_hours: int


class UserMeResponse(BaseModel):
    id: int
    email: str
    display_name: str
    roles: List[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
