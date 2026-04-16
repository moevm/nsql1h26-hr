from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, HttpUrl, ConfigDict
from pydantic_extra_types.phone_numbers import PhoneNumber


class CandidateStatus(StrEnum):
    NEW = "NEW"
    TEST = "TEST"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    HIRED = "HIRED"


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
