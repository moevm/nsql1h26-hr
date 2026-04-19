from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, HttpUrl, ConfigDict
from pydantic_extra_types.phone_numbers import PhoneNumber
from app.models.unix_timestamp import UnixTimestamp
from app.models.helpers import SortOrder
from typing import List


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
    phone: PhoneNumber
    resume_url: HttpUrl | None = None
    status: CandidateStatus
    vacancy_id: UUID | None = None
    test_task_id: UUID | None = None

    model_config = ConfigDict(from_attributes=True)


class CandidateResponse(BaseModel):
    id: UUID
    full_name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    phone: PhoneNumber
    resume_url: HttpUrl | None = None
    status: CandidateStatus
    vacancy_id: UUID | None = None
    test_task_id: UUID | None = None

    model_config = ConfigDict(from_attributes=True)


class CandidateFilter(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=150)
    email: EmailStr | None = None
    phone: PhoneNumber | None = None
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
