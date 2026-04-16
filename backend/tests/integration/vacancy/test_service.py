import pytest
from datetime import datetime
from app.models.vacancy import VacancyCreate, VacancyStatus
from app.services.vacancy_service import VacancyService
from app.repositories.vacancy_repo import VacancyRepository


@pytest.fixture
def vacancy_service(neo4j_driver):
    return VacancyService(VacancyRepository(neo4j_driver))


async def test_create_vacancy(vacancy_service):
    test_vacancy = VacancyCreate(
        title="Test vacancy",
        description="Test Vacancy Description"
    )
    vacancy = await vacancy_service.create_vacancy(test_vacancy)
    assert vacancy.title == test_vacancy.title
    assert vacancy.status == VacancyStatus.OPEN
    assert vacancy.description == test_vacancy.description
    assert vacancy.created_at
