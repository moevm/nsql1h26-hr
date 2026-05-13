import pytest
from app.models.vacancy import VacancyCreate
from app.models.test_task import TestTaskCreate, TestTasksFilter, TestTaskPatch
from app.core.exceptions import AppError


async def test_create_test_task_ok(test_task_service, vacancy_service):
    test_vacancy = VacancyCreate(
        title="Test vacancy", description="Test Vacancy Description"
    )
    vacancy = await vacancy_service.create_vacancy(test_vacancy)
    test_task = TestTaskCreate(
        title="test task 1", test_task_url="https://google.com", vacancy_id=vacancy.id
    )

    got_test_task = await test_task_service.create_test_task(test_task)
    assert got_test_task.title == test_task.title
    assert got_test_task.test_task_url == test_task.test_task_url
    assert got_test_task.vacancy_id == vacancy.id
    assert got_test_task.id is not None


async def test_get_test_task_by_id(test_task_service, vacancy_service):
    test_vacancy = VacancyCreate(
        title="Test vacancy", description="Test Vacancy Description"
    )
    vacancy = await vacancy_service.create_vacancy(test_vacancy)
    test_task = TestTaskCreate(
        title="test task 1", test_task_url="https://google.com", vacancy_id=vacancy.id
    )
    created_test_task = await test_task_service.create_test_task(test_task)

    got_test_task = await test_task_service.get_test_task_by_id(created_test_task.id)
    assert got_test_task == created_test_task


async def test_filter_test_tasks(test_task_service, vacancy_service):
    test_vacancy = VacancyCreate(
        title="Test vacancy", description="Test Vacancy Description"
    )
    vacancy = await vacancy_service.create_vacancy(test_vacancy)
    test_tasks_data = [
        TestTaskCreate(
            title="test task 1",
            test_task_url="https://google.com",
            vacancy_id=vacancy.id,
        ),
        TestTaskCreate(
            title="test task 2", test_task_url="https://ggle.com", vacancy_id=vacancy.id
        ),
    ]
    created_tasks = []
    for task_data in test_tasks_data:
        created_tasks.append(await test_task_service.create_test_task(task_data))

    filters = TestTasksFilter()
    result = await test_task_service.filter_test_tasks(filters)

    assert result.total == len(test_tasks_data)
    expected_sorted = sorted(created_tasks, key=lambda x: x.title, reverse=False)
    assert result.items == expected_sorted


async def test_patch_test_tesk_full(test_task_service, vacancy_service):
    test_vacancy = VacancyCreate(
        title="Test vacancy", description="Test Vacancy Description"
    )
    vacancy = await vacancy_service.create_vacancy(test_vacancy)
    test_task = TestTaskCreate(
        title="test task 1", test_task_url="https://google.com", vacancy_id=vacancy.id
    )

    created_test_task = await test_task_service.create_test_task(test_task)
    patch_test_task = TestTaskPatch(
        title="New test", test_task_url="https://kawaii.com"
    )

    patched_test_task = await test_task_service.patch_test_task(
        created_test_task.id, patch_test_task
    )

    assert patched_test_task.title == patch_test_task.title
    assert patched_test_task.test_task_url == patch_test_task.test_task_url
    assert patched_test_task.vacancy_id == vacancy.id
    assert patched_test_task.id is not None


async def test_patch_test_tesk_empty(test_task_service, vacancy_service):
    test_vacancy = VacancyCreate(
        title="Test vacancy", description="Test Vacancy Description"
    )
    vacancy = await vacancy_service.create_vacancy(test_vacancy)
    test_task = TestTaskCreate(
        title="test task 1", test_task_url="https://google.com", vacancy_id=vacancy.id
    )

    created_test_task = await test_task_service.create_test_task(test_task)
    patch_test_task = TestTaskPatch()

    patched_test_task = await test_task_service.patch_test_task(
        created_test_task.id, patch_test_task
    )

    assert patched_test_task.title == test_task.title
    assert patched_test_task.test_task_url == test_task.test_task_url
    assert patched_test_task.vacancy_id == vacancy.id
    assert patched_test_task.id is not None


async def test_patch_test_tesk_bad_id(test_task_service, vacancy_service):
    test_vacancy = VacancyCreate(
        title="Test vacancy", description="Test Vacancy Description"
    )
    vacancy = await vacancy_service.create_vacancy(test_vacancy)
    test_task = TestTaskCreate(
        title="test task 1", test_task_url="https://google.com", vacancy_id=vacancy.id
    )

    created_test_task = await test_task_service.create_test_task(test_task)
    patch_test_task = TestTaskPatch()
    with pytest.raises(AppError):
        await test_task_service.patch_test_task(vacancy.id, patch_test_task)
