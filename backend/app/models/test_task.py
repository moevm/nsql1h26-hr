from uuid import UUID
from enum import StrEnum
from pydantic import BaseModel, Field, HttpUrl
from app.models.helpers import SortOrder
from typing import List


class TestTaskSort(StrEnum):
    TITLE = "title"
    VACANCY_ID = "vacancy_id"
    CREATED_AT = "created_at"


class TestTaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    test_task_url: HttpUrl
    vacancy_id: UUID


class TestTaskResponse(BaseModel):
    id: UUID
    title: str = Field(min_length=1, max_length=100)
    test_task_url: HttpUrl
    vacancy_id: UUID


class TestTaskPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    test_task_url: HttpUrl | None = None


class TestTasksFilter(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    vacancy_id: UUID | None = None
    vacancy_title: str | None = Field(default=None, min_length=1, max_length=100)
    test_task_url_contains: str | None = None
    has_assigned_candidates: bool | None = None
    limit: int | None = Field(default=50, ge=1, le=200)
    offset: int | None = Field(default=0, ge=0)
    sort_by: TestTaskSort | None = TestTaskSort.TITLE
    sort_order: SortOrder | None = SortOrder.ASC


class TestTasksFilterResponse(BaseModel):
    total: int = Field(ge=0)
    items: List[TestTaskResponse]
