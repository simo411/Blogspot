"""Request/response shapes. Responses never include password hashes."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def fits_bcrypt(cls, v: str) -> str:
        if len(v.encode()) > 72:
            raise ValueError("password must be at most 72 bytes")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    """What other people may see about a user (e.g. blog authors)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    username: str
    avatar: int | None


class UserMe(UserPublic):
    """What a logged-in user sees about themselves."""

    email: EmailStr
    created_at: datetime


class AvatarUpdate(BaseModel):
    avatar: int = Field(ge=1, le=5)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserMe


class BlogCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=100_000)


class BlogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    created_at: datetime
    author: UserPublic
