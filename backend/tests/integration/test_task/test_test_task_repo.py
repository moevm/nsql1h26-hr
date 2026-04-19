import pytest
from app.repositories.test_task_repo import TestTaskRepository
from app.repositories.vacancy_repo import VacancyRepository
from app.models.vacancy import VacancyCreate
from app.models.test_task import TestTaskCreate


@pytest.fixture
def test_task_repo(neo4j_driver):
    return TestTaskRepository(neo4j_driver)


@pytest.fixture
def vacancy_repo(neo4j_driver):
    return VacancyRepository(neo4j_driver)


async def test_create_test_task(test_task_repo, vacancy_repo):
    vacancy_id = (
        await vacancy_repo.create_vacancy(
            VacancyCreate(title="Title1", description="desc")
        )
    )["id"]
    test_task = TestTaskCreate(
        title="Test title 1", test_task_url="https://google.com", vacancy_id=vacancy_id
    )
    got_test_task = await test_task_repo.create_test_task(test_task)
    assert got_test_task["id"] is not None
    assert got_test_task["title"] == test_task.title
    assert got_test_task["vacancy_id"] == vacancy_id
    assert got_test_task["test_task_url"] == str(test_task.test_task_url)


async def test_get_test_task_by_id(test_task_repo, vacancy_repo):
    vacancy_id = (
        await vacancy_repo.create_vacancy(
            VacancyCreate(title="Title1", description="desc")
        )
    )["id"]
    test_task = TestTaskCreate(
        title="Test title 1",
        test_task_url="https://google.com",
        vacancy_id=vacancy_id
    )
    created_test_task = await test_task_repo.create_test_task(test_task)
    test_task_id = created_test_task["id"]

    got_test_task = await test_task_repo.get_test_task_by_id(test_task_id)
    assert got_test_task["id"] == test_task_id
    assert got_test_task["title"] == test_task.title
    assert got_test_task["vacancy_id"] == vacancy_id
    assert got_test_task["test_task_url"] == str(test_task.test_task_url)
