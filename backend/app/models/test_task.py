from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl


class TestTaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    test_task_url: HttpUrl
    vacancy_id: UUID


class TestTaskResponse(BaseModel):
    id: UUID
    title: str = Field(min_length=1, max_length=100)
    test_task_url: HttpUrl
    vacancy_id: UUID
