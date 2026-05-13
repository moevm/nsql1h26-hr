import pytest
from app.models.vacancy import VacancyCreate, VacancyPatch, VacancyStatus, VacancyFilter
from collections import Counter


async def test_create_vacancy(vacancy_service):
    test_vacancy = VacancyCreate(
        title="Test vacancy", description="Test Vacancy Description"
    )
    vacancy = await vacancy_service.create_vacancy(test_vacancy)
    assert vacancy.title == test_vacancy.title
    assert vacancy.status == VacancyStatus.OPEN
    assert vacancy.description == test_vacancy.description
    assert vacancy.created_at


async def test_get_vacancy_by_id(vacancy_service):
    test_vacancy = VacancyCreate(
        title="Test vacancy", description="Test Vacancy Description"
    )
    created_vacancy = await vacancy_service.create_vacancy(test_vacancy)
    found_vacancy = await vacancy_service.get_vacancy_by_id(created_vacancy.id)
    assert found_vacancy is not None
    assert found_vacancy == created_vacancy


async def test_patch_vacancy_ok(vacancy_service):
    test_vacancy = VacancyCreate(
        title="Test vacancy", description="Test Vacancy Description"
    )
    vacancy = await vacancy_service.create_vacancy(test_vacancy)
    vacancy_patch = VacancyPatch()
    vacancy_patch.status = VacancyStatus.CLOSED
    patched_vacancy = await vacancy_service.patch_vacancy(vacancy.id, vacancy_patch)
    assert patched_vacancy is not None
    assert patched_vacancy.title == vacancy.title
    assert patched_vacancy.status == VacancyStatus.CLOSED
    assert patched_vacancy.closed_at is not None


async def test_patch_vacancy_ok2(vacancy_service):
    test_vacancy = VacancyCreate(
        title="Test vacancy", description="Test Vacancy Description"
    )
    vacancy = await vacancy_service.create_vacancy(test_vacancy)
    vacancy_patch = VacancyPatch()
    vacancy_patch.title = "Title 2"
    vacancy_patch.description = "D 2"
    patched_vacancy = await vacancy_service.patch_vacancy(vacancy.id, vacancy_patch)
    assert patched_vacancy is not None
    assert patched_vacancy.title == vacancy_patch.title
    assert patched_vacancy.description == vacancy_patch.description
    assert patched_vacancy.status == VacancyStatus.OPEN
    assert patched_vacancy.closed_at is None


async def test_filter_vacancies(vacancy_service):
    test_vacancies = [
        VacancyCreate(title="Test vacancy 1", description="Test Vacancy Description 1"),
        VacancyCreate(title="Test vacancy 2", description="Test Vacancy Description 2"),
    ]

    expected = []
    for vacancy in test_vacancies:
        expected.append(await vacancy_service.create_vacancy(vacancy))
    filters = VacancyFilter()
    got_vacancies = await vacancy_service.filter_vacancies(filters)
    assert got_vacancies.total == len(test_vacancies)
    expected_sorted = sorted(expected, key=lambda x: x.created_at, reverse=True)
    assert got_vacancies.items == expected_sorted
