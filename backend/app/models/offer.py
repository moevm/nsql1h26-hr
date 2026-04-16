from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, NonNegativeInt, ConfigDict
from app.models.unix_timestamp import UnixTimestamp


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
    status: OfferStatus = OfferStatus.PENDING

    model_config = ConfigDict(from_attributes=True)
