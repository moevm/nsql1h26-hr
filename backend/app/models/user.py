from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


class Role(StrEnum):
    ADMIN = "ADMIN"
    HR = "HR"
    TECH_SPEC = "TECH_SPEC"
    MANAGER = "MANAGER"


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=3, max_length=150)
    role: Role


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str = Field(min_length=3, max_length=150)
    role: Role


class UserDB(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str = Field(min_length=3, max_length=150)
    role: Role
    password_hash: str
