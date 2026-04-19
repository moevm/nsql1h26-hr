from fastapi import APIRouter, status, Depends
from neo4j import AsyncDriver
from uuid import UUID
from app.core.database import get_db
from app.services.test_task_service import TestTaskService
from app.repositories.vacancy_repo import VacancyRepository
from app.repositories.test_task_repo import TestTaskRepository
from app.models.test_task import TestTaskCreate, TestTaskResponse

router = APIRouter()


def get_test_task_service(driver: AsyncDriver = Depends(get_db)) -> TestTaskService:
    vacancy_repo = VacancyRepository(driver)
    test_task_repo = TestTaskRepository(driver)
    return TestTaskService(test_task_repo, vacancy_repo)


@router.post("",
             response_model=TestTaskResponse,
             status_code=status.HTTP_201_CREATED)
async def create_test_task(
    test_task_data: TestTaskCreate,
    test_task_service: TestTaskService = Depends(get_test_task_service),
):
    test_task = await test_task_service.create_test_task(test_task_data)
    return test_task


@router.get(
    "/{test_task_id}",
    response_model=TestTaskResponse,
    status_code=status.HTTP_200_OK
)
async def get_test_task_by_id(
    test_task_id: UUID,
    test_task_service: TestTaskService = Depends(get_test_task_service),
):
    test_task = await test_task_service.get_test_task_by_id(test_task_id)
    return test_task
