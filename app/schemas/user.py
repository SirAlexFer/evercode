from typing import Optional

from pydantic import EmailStr, Field
from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(title="Username")
    full_name: str = Field(title="Full Name")


class UserCreate(UserBase):
    password: str = Field(title="Password")


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr = Field(title="Email")
    password: str = Field(title="Password")


class TwoTokens(BaseModel):
    access_token: str
    refresh_token: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    model_config = ConfigDict(from_attributes=True)
