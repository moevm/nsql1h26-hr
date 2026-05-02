from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, HttpUrl, ConfigDict, field_validator
from typing import List
from app.models.unix_timestamp import UnixTimestamp
from app.models.helpers import SortOrder


class CandidateStatus(StrEnum):
    NEW = "NEW"
    TEST = "TEST"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    HIRED = "HIRED"


class CandidateSort(StrEnum):
    FULL_NAME = "full_name"
    EMAIL = "email"
    STATUS = "status"
    CREATED_AT = "created_at"


class CandidateCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    phone: str  # workaround
    resume_url: HttpUrl | None = None
    status: CandidateStatus
    vacancy_id: UUID | None = None
    test_task_id: UUID | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not v.startswith("+7") or len(v) != 12 or not v[1:].isdigit():
            raise ValueError(
                "Phone number must be in format +7XXXXXXXXXX (10 digits after +7)"
            )
        return v

    model_config = ConfigDict(from_attributes=True)


class CandidateResponse(BaseModel):
    id: UUID
    full_name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    phone: str
    resume_url: HttpUrl | None = None
    status: CandidateStatus
    vacancy_id: UUID | None = None
    test_task_id: UUID | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not v.startswith("+7") or len(v) != 12 or not v[1:].isdigit():
            raise ValueError(
                "Phone number must be in format +7XXXXXXXXXX (10 digits after +7)"
            )
        return v

    model_config = ConfigDict(from_attributes=True)


class CandidateFilter(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=150)
    email: EmailStr | None = None
    phone: str | None = None
    resume_url_contains: HttpUrl | None = None
    status: CandidateStatus | None = None
    vacancy_id: UUID | None = None
    vacancy_title: str | None = Field(default=None, min_length=1, max_length=100)
    test_task_id: UUID | None = None
    test_task_title: str | None = Field(default=None, min_length=1, max_length=100)
    created_at_from: UnixTimestamp | None = None
    created_at_to: UnixTimestamp | None = None
    has_interview: bool | None = None
    has_offer: bool | None = None
    limit: int | None = Field(default=50, ge=1, le=200)
    offset: int | None = Field(default=0, ge=0)
    sort_by: CandidateSort | None = CandidateSort.FULL_NAME
    sort_order: SortOrder | None = SortOrder.DESC


class CandidateFilterResponse(BaseModel):
    total: int = Field(ge=0)
    items: List[CandidateResponse]
