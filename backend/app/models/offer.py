from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, NonNegativeInt, ConfigDict, Field
from app.models.unix_timestamp import UnixTimestamp
from app.models.candidate import CandidateStatus


class OfferStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED_MNG = "APPROVED_MNG"
    REJECTED_MNG = "REJECTED_MNG"
    APPROVED_CND = "APPROVED_CND"
    REJECTED_CNF = "REJECTED_CNF"


class OfferCreate(BaseModel):
    candidate_id: UUID
    vacancy_id: UUID
    created_by: UUID
    salary: NonNegativeInt
    start_at: UnixTimestamp
    status: OfferStatus | None = OfferStatus.PENDING

    model_config = ConfigDict(from_attributes=True)


class OfferResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    vacancy_id: UUID
    created_by: UUID
    salary: NonNegativeInt
    start_at: UnixTimestamp
    created_at: UnixTimestamp
    status: OfferStatus = OfferStatus.PENDING

    model_config = ConfigDict(from_attributes=True)


class OfferPatch(BaseModel):
    status: OfferStatus


class OfferSort(StrEnum):
    SALARY = "salary"
    START_AT = "start_at"
    STATUS = "status"
    CREATED_AT = "created_at"
    CANDIDATE_NAME = "candidate_name"
    VACANCY_TITLE = "vacancy_title"


class OfferFilter(BaseModel):
    salary_from: int | None = Field(default=None, ge=0)
    salary_to: int | None = Field(default=None, ge=0)
    status: OfferStatus | None = None
    start_at_from: UnixTimestamp | None = None
    start_at_to: UnixTimestamp | None = None
    candidate_id: UUID | None = None
    candidate_name: str | None = Field(default=None, min_length=1, max_length=150)
    candidate_email: str | None = Field(default=None, min_length=1, max_length=255)
    candidate_status: CandidateStatus | None = None
    vacancy_id: UUID | None = None
    vacancy_title: str | None = Field(default=None, min_length=1, max_length=100)
    vacancy_status: str | None = None
    created_by: UUID | None = None
    created_by_name: str | None = Field(default=None, min_length=1, max_length=150)
    created_at_from: UnixTimestamp | None = None
    created_at_to: UnixTimestamp | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
    sort_by: OfferSort = OfferSort.CREATED_AT
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")

    model_config = ConfigDict(from_attributes=True)


class OfferFilterResponse(BaseModel):
    total: int
    items: list[OfferResponse]

    model_config = ConfigDict(from_attributes=True)
