
from app.models.test_task import TestTaskCreate, TestTaskResponse
from app.repositories.vacancy_repo import VacancyRepository
from app.repositories.test_task_repo import TestTaskRepository
from app.core.exceptions import AppError
from fastapi import status


class TestTaskService:
    def __init__(self, 
                 test_task_repo: TestTaskRepository, 
                 vacancy_repo: VacancyRepository):
        self.test_task_repo = test_task_repo
        self.vacancy_repo = vacancy_repo

    
    async def create_test_task(self, test_task_data: TestTaskCreate) -> TestTaskResponse:
        vacancy_id = test_task_data.vacancy_id
        vacancy = await self.vacancy_repo.get_vacancy_by_id(vacancy_id)
        if vacancy is None:
            raise AppError("Cannot create test task for unexisting vacancy",
                           status.HTTP_404_NOT_FOUND)
        created_test_task = await self.test_task_repo.create_test_task(test_task_data)
        return TestTaskResponse(**created_test_task)
