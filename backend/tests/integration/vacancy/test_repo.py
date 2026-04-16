import pytest
from datetime import datetime
from app.models.vacancy import VacancyCreate, VacancyStatus
from app.repositories.vacancy_repo import VacancyRepository


@pytest.fixture
def vacancy_repo(neo4j_driver):
    return VacancyRepository(neo4j_driver)


async def test_create_vacancy(vacancy_repo):
    test_vacancy = VacancyCreate(
        title="Test vacancy",
        status=VacancyStatus.OPEN,
        description="Test Vacancy Description",
        created_at=datetime.now(),
    )
    vacancy = await vacancy_repo.create_vacancy(test_vacancy)
    assert vacancy["title"] == test_vacancy.title
    assert vacancy["status"] == test_vacancy.status
    assert vacancy["description"] == test_vacancy.description
    assert vacancy["created_at"] == test_vacancy.created_at
