from enum import StrEnum
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from app.models.helpers import SortOrder


class Role(StrEnum):
    ADMIN = "ADMIN"
    HR = "HR"
    TECH_SPEC = "TECH_SPEC"
    MANAGER = "MANAGER"


class UserSort(StrEnum):
    EMAIL = "email"
    FULL_NAME = "full_name"
    ROLE = "role"


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=5, max_length=100)
    role: Role


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str = Field(min_length=3, max_length=150)
    role: Role

    model_config = ConfigDict(from_attributes=True)


class UserDB(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str = Field(min_length=3, max_length=150)
    role: Role
    password_hash: str

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserFilter(BaseModel):
    email: str | None = Field(default=None, min_length=1, max_length=100)
    full_name: str | None = Field(default=None, min_length=1, max_length=150)
    role: Role | None = None
    limit: int | None = Field(default=50, ge=1, le=200)
    offset: int | None = Field(default=0, ge=0)
    sort_by: UserSort | None = UserSort.EMAIL
    sort_order: SortOrder | None = SortOrder.ASC


class UserFilterResponse(BaseModel):
    total: int = Field(ge=0)
    items: List[UserResponse]
