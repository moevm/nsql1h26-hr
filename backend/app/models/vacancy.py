from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.models.unix_timestamp import UnixTimestamp
from app.models.helpers import SortOrder
from typing import List


class VacancyStatus(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class VacancySort(StrEnum):
    TITLE = "title"
    STATUS = "status"
    CREATED_AT = "created_at"
    CLOSED_AT = "closed_at"


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


class VacancyFilter(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description_contains: str | None = Field(
        default=None, min_length=1, max_length=5000
    )
    status: VacancyStatus | None = None
    created_at_from: UnixTimestamp | None = None
    created_at_to: UnixTimestamp | None = None
    closed_at_from: UnixTimestamp | None = None
    closed_at_to: UnixTimestamp | None = None
    has_test_task: bool | None = None
    limit: int | None = Field(default=50, ge=1, le=200)
    offset: int | None = Field(default=0, ge=0)
    sort_by: VacancySort | None = VacancySort.CREATED_AT
    sort_order: SortOrder | None = SortOrder.DESC


class VacancyFilterResponse(BaseModel):
    total: int = Field(ge=0)
    items: List[VacancyResponse]
