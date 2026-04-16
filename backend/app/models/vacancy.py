from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.models.unix_timestamp import UnixTimestamp


class VacancyStatus(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class VacancyCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=5000)
    status: VacancyStatus | None = None
    created_at: UnixTimestamp | None = None
    closed_at: UnixTimestamp | None = None

    model_config = ConfigDict(from_attributes=True)


class VacancyResponse(BaseModel):
    id: UUID
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=5000)
    status: VacancyStatus = VacancyStatus.OPEN
    created_at: UnixTimestamp
    closed_at: UnixTimestamp | None = None

    model_config = ConfigDict(from_attributes=True)


class VacancyPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=5000)
    status: VacancyStatus | None = VacancyStatus.OPEN
    closed_at: UnixTimestamp | None = None
