import pytest
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


async def test_get_vacancy_by_id(vacancy_service):
    test_vacancy = VacancyCreate(
        title="Test vacancy",
        description="Test Vacancy Description"
    )
    created_vacancy = await vacancy_service.create_vacancy(test_vacancy)
    found_vacancy = await vacancy_service.get_vacancy_by_id(created_vacancy.id)
    assert found_vacancy is not None
    assert found_vacancy == created_vacancy
