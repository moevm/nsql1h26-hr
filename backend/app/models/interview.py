from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from app.models.unix_timestamp import UnixTimestamp


class InterviewResult(StrEnum):
    AWAIT_INTERVIEW = "AWAIT_INTERVIEW"
    INTERVIEW_PASSED = "INTERVIEW_PASSED"
    INTERVIEW_FAILED = "INTERVIEW_FAILED"


class InterviewCreate(BaseModel):
    candidate_id: UUID
    tech_spec_id: UUID
    scheduled_at: UnixTimestamp
    zoom_url: HttpUrl | None = None
    feedback: str | None = Field(default=None, min_length=1, max_length=2000)
    result: InterviewResult | None = InterviewResult.AWAIT_INTERVIEW

    model_config = ConfigDict(from_attributes=True)


class InterviewResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    tech_spec_id: UUID
    scheduled_at: UnixTimestamp
    zoom_url: HttpUrl | None = None
    feedback: str | None = Field(default=None, min_length=1, max_length=2000)
    result: InterviewResult | None = InterviewResult.AWAIT_INTERVIEW

    model_config = ConfigDict(from_attributes=True)
