import datetime

from pydantic.v1 import BaseModel, Field

from config import settings


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=30)
    phone: str = Field(..., max_length=20)
    email: str = Field(..., max_length=25)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)

class UserLogin(BaseModel):
    email: str = Field(..., max_length=25)
    password: str = Field(..., min_length=6, max_length=128)

class UserUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=30)
    phone: str = Field(..., max_length=20)

class UserResponse(UserBase):
    id: int
    created_at: datetime

class AccessToken(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

class RefreshToken(AccessToken):
    refresh_token: str
    refresh_expires_in: int = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 24 * 3600
