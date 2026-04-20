from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from app.models.unix_timestamp import UnixTimestamp
from app.models.helpers import SortOrder


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


class InterviewSort(StrEnum):
    SCHEDULED_AT = "scheduled_at"
    RESULT = "result"
    CANDIDATE_NAME = "candidate_name"
    TECH_SPEC_NAME = "tech_spec_name"


class InterviewFilter(BaseModel):
    candidate_id: UUID | None = None
    candidate_name: str | None = Field(default=None, min_length=1, max_length=150)
    tech_spec_id: UUID | None = None
    tech_spec_name: str | None = Field(default=None, min_length=1, max_length=150)
    result: InterviewResult | None = None
    feedback_contains: str | None = Field(default=None, min_length=1, max_length=2000)
    scheduled_at_from: UnixTimestamp | None = None
    scheduled_at_to: UnixTimestamp | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
    sort_by: InterviewSort = InterviewSort.SCHEDULED_AT
    sort_order: SortOrder | None = SortOrder.DESC

    model_config = ConfigDict(from_attributes=True)


class InterviewFilterResponse(BaseModel):
    total: int
    items: list[InterviewResponse]

    model_config = ConfigDict(from_attributes=True)
