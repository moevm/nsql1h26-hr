import pytest
import uuid
from app.models.vacancy import VacancyCreate
from app.models.test_task import TestTaskCreate, TestTaskResponse
from app.services.test_task_service import TestTaskService
from app.services.vacancy_service import VacancyService
from app.repositories.test_task_repo import TestTaskRepository
from app.repositories.vacancy_repo import VacancyRepository



@pytest.fixture
def vacancy_service(neo4j_driver):
    return VacancyService(VacancyRepository(neo4j_driver))


@pytest.fixture
def test_task_service(neo4j_driver):
    return TestTaskService(TestTaskRepository(neo4j_driver), VacancyRepository(neo4j_driver))


async def test_create_test_task_ok(test_task_service, vacancy_service):
    test_vacancy = VacancyCreate(
        title="Test vacancy",
        description="Test Vacancy Description"
    )
    vacancy = await vacancy_service.create_vacancy(test_vacancy)
    test_task = TestTaskCreate(
        title="test task 1",
        test_task_url="https://google.com",
        vacancy_id=vacancy.id
    )

    got_test_task = await test_task_service.create_test_task(test_task)
    assert got_test_task.title == test_task.title
    assert got_test_task.test_task_url == test_task.test_task_url
    assert got_test_task.vacancy_id == vacancy.id
    assert got_test_task.id is not None
