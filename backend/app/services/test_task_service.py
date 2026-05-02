from app.models.test_task import (
    TestTaskCreate,
    TestTaskResponse,
    TestTasksFilter,
    TestTasksFilterResponse,
)
from app.repositories.vacancy_repo import VacancyRepository
from app.repositories.test_task_repo import TestTaskRepository
from app.core.exceptions import AppError
from fastapi import status
from uuid import UUID


class TestTaskService:
    def __init__(
        self, test_task_repo: TestTaskRepository, vacancy_repo: VacancyRepository
    ):
        self.test_task_repo = test_task_repo
        self.vacancy_repo = vacancy_repo

    async def create_test_task(
        self, test_task_data: TestTaskCreate
    ) -> TestTaskResponse:
        vacancy_id = test_task_data.vacancy_id
        vacancy = await self.vacancy_repo.get_vacancy_by_id(vacancy_id)
        if vacancy is None:
            raise AppError(
                "Cannot create test task for unexisting vacancy",
                status.HTTP_404_NOT_FOUND,
            )
        created_test_task = await self.test_task_repo.create_test_task(test_task_data)
        return TestTaskResponse(**created_test_task)

    async def get_test_task_by_id(self, test_task_id: UUID) -> TestTaskResponse:
        test_task = await self.test_task_repo.get_test_task_by_id(test_task_id)
        if test_task is None:
            raise AppError(
                "Test task with given UUID not found",
                status.HTTP_404_NOT_FOUND,
            )
        return TestTaskResponse(**test_task)

    async def filter_test_tasks(
        self, filters: TestTasksFilter
    ) -> TestTasksFilterResponse:
        filters = await self.test_task_repo.filter_test_tasks(filters)
        return TestTasksFilterResponse(**filters)
