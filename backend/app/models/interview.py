from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from pydantic_extra_types.phone_numbers import PhoneNumber


class InterviewResult(StrEnum):
    AWAIT_INTERVIEW = "AWAIT_INTERVIEW"
    INTERVIEW_PASSED = "INTERVIEW_PASSED"
    INTERVIEW_FAILED = "INTERVIEW_FAILED"


class InterviewCreate(BaseModel):
    candidate_id: UUID
    tech_spec_id: UUID
    scheduled_at: int
    zoom_url: HttpUrl | None = None
    feedback: str | None = Field(default=None, min_length=1, max_length=2000)
    result: InterviewResult | None = InterviewResult.AWAIT_INTERVIEW


class InterviewResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    tech_spec_id: UUID
    scheduled_at: int
    zoom_url: HttpUrl | None = None
    feedback: str | None = Field(default=None, min_length=1, max_length=2000)
    result: InterviewResult | None = InterviewResult.AWAIT_INTERVIEW
