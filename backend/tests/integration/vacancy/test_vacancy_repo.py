import pytest
from datetime import datetime
from uuid import UUID
from app.models.vacancy import VacancyCreate, VacancyStatus, VacancyResponse, VacancyFilter
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


async def create_vacancy(vacancy_repo, vacancy: VacancyCreate) -> dict:
    created_vacancy = await vacancy_repo.create_vacancy(vacancy)
    return created_vacancy


async def test_get_vacancy_by_id(vacancy_repo):
    test_vacancy = VacancyCreate(
        title="Test vacancy",
        status=VacancyStatus.OPEN,
        description="Test Vacancy Description",
        created_at=datetime.now(),
    )
    created_vacancy = await create_vacancy(vacancy_repo, test_vacancy)
    vacancy_id = created_vacancy["id"]

    found_vacancy = await vacancy_repo.get_vacancy_by_id(vacancy_id)
    assert found_vacancy is not None
    assert found_vacancy == created_vacancy


async def test_patch_vacancy_ok(vacancy_repo):
    test_vacancy = VacancyCreate(
        title="Test vacancy",
        status=VacancyStatus.OPEN,
        description="Test Vacancy Description",
        created_at=datetime.now(),
    )
    created_vacancy = await vacancy_repo.create_vacancy(test_vacancy)
    vacancy_id = created_vacancy["id"]
    created_vacancy["status"] = "CLOSED"
    created_vacancy["closed_at"] = str(int(datetime.now().timestamp()))

    found_vacancy = await vacancy_repo.patch_vacancy(vacancy_id,
                                                     {"status": "CLOSED",
                                                      "closed_at": created_vacancy["closed_at"]})
    assert found_vacancy is not None
    assert found_vacancy == created_vacancy


async def test_filter_vacancy_all(vacancy_repo):
    vacancies = [VacancyCreate(
        title="Test vacancy 1",
        status=VacancyStatus.OPEN,
        description="Test Vacancy Description 1",
        created_at=datetime.now(),
    ),
    VacancyCreate(
        title="Test vacancy 2",
        status=VacancyStatus.OPEN,
        description="Test Vacancy Description 2",
        created_at=datetime.now(),
    )]
    expected_ids = set()
    for vacancy in vacancies:
        expected_ids.add((await create_vacancy(vacancy_repo, vacancy))["id"])
    filters = VacancyFilter()
    got_vacancies = await vacancy_repo.filter_vacancies(filters)
    assert got_vacancies["total"] == 2
    got_ids = {v['id'] for v in got_vacancies["items"]}
    assert got_ids == expected_ids
