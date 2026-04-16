from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, Field


class VacancyStatus(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class VacancyCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=5000)
    status: VacancyStatus | None = None
    created_at: int | None = None
    closed_at: int | None = None


class VacancyResponse(BaseModel):
    id: UUID
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=5000)
    status: VacancyStatus = VacancyStatus.OPEN
    created_at: int
    closed_at: int | None = None
