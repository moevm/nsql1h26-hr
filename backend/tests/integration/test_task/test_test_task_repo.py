import pytest
from app.models.vacancy import VacancyCreate
from app.models.test_task import (
    TestTaskCreate,
    TestTaskSort,
    TestTasksFilter,
)


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
        title="Test title 1", test_task_url="https://google.com", vacancy_id=vacancy_id
    )
    created_test_task = await test_task_repo.create_test_task(test_task)
    test_task_id = created_test_task["id"]

    got_test_task = await test_task_repo.get_test_task_by_id(test_task_id)
    assert got_test_task["id"] == test_task_id
    assert got_test_task["title"] == test_task.title
    assert got_test_task["vacancy_id"] == vacancy_id
    assert got_test_task["test_task_url"] == str(test_task.test_task_url)


async def test_filter_by_vacancy_id(test_task_repo, vacancy_repo):
    v1_id = (
        await vacancy_repo.create_vacancy(VacancyCreate(title="V1", description="D1"))
    )["id"]
    v2_id = (
        await vacancy_repo.create_vacancy(VacancyCreate(title="V2", description="D2"))
    )["id"]

    await test_task_repo.create_test_task(
        TestTaskCreate(title="T1", test_task_url="http://1.com", vacancy_id=v1_id)
    )
    await test_task_repo.create_test_task(
        TestTaskCreate(title="T2", test_task_url="http://2.com", vacancy_id=v2_id)
    )

    filters = TestTasksFilter(vacancy_id=v1_id)
    result = await test_task_repo.filter_test_tasks(filters)

    assert result["total"] == 1
    assert result["items"][0]["vacancy_id"] == v1_id
    assert result["items"][0]["title"] == "T1"


async def test_filter_by_title_substring(test_task_repo, vacancy_repo):
    v1_id = (
        await vacancy_repo.create_vacancy(VacancyCreate(title="V1", description="D1"))
    )["id"]
    v2_id = (
        await vacancy_repo.create_vacancy(VacancyCreate(title="V2", description="D2"))
    )["id"]

    await test_task_repo.create_test_task(
        TestTaskCreate(
            title="Python Developer", test_task_url="http://1.com", vacancy_id=v1_id
        )
    )
    await test_task_repo.create_test_task(
        TestTaskCreate(
            title="Frontend Lead", test_task_url="http://2.com", vacancy_id=v2_id
        )
    )

    filters = TestTasksFilter(title="DEV")
    result = await test_task_repo.filter_test_tasks(filters)

    assert result["total"] == 1
    assert "Python Developer" in result["items"][0]["title"]


async def test_filter_by_vacancy_title(test_task_repo, vacancy_repo):
    v1_id = (
        await vacancy_repo.create_vacancy(
            VacancyCreate(title="Backend Ruby", description="D1")
        )
    )["id"]
    v2_id = (
        await vacancy_repo.create_vacancy(
            VacancyCreate(title="Data Science", description="D2")
        )
    )["id"]

    await test_task_repo.create_test_task(
        TestTaskCreate(title="Test 1", test_task_url="http://1.com", vacancy_id=v1_id)
    )
    await test_task_repo.create_test_task(
        TestTaskCreate(title="Test 2", test_task_url="http://2.com", vacancy_id=v2_id)
    )

    filters = TestTasksFilter(vacancy_title="Ruby")
    result = await test_task_repo.filter_test_tasks(filters)

    assert result["total"] == 1
    assert result["items"][0]["vacancy_id"] == v1_id


async def test_sorting_and_pagination(test_task_repo, vacancy_repo):
    v_id = (
        await vacancy_repo.create_vacancy(VacancyCreate(title="V", description="D"))
    )["id"]

    for t in ["A-task", "B-task", "C-task"]:
        await test_task_repo.create_test_task(
            TestTaskCreate(title=t, test_task_url="http://test.com", vacancy_id=v_id)
        )

    filters = TestTasksFilter(
        sort_by=TestTaskSort.TITLE, sort_order="desc", limit=2, offset=0
    )
    result = await test_task_repo.filter_test_tasks(filters)

    assert result["total"] == 3
    assert len(result["items"]) == 2
    assert result["items"][0]["title"] == "C-task"
    assert result["items"][1]["title"] == "B-task"


async def test_url_contains_filter(test_task_repo, vacancy_repo):
    v_id = (
        await vacancy_repo.create_vacancy(VacancyCreate(title="V", description="D"))
    )["id"]

    await test_task_repo.create_test_task(
        TestTaskCreate(title="T1", test_task_url="https://github.com", vacancy_id=v_id)
    )
    await test_task_repo.create_test_task(
        TestTaskCreate(title="T2", test_task_url="https://gitlab.com", vacancy_id=v_id)
    )

    filters = TestTasksFilter(test_task_url_contains="github")
    result = await test_task_repo.filter_test_tasks(filters)

    assert result["total"] == 1
    assert "github.com" in result["items"][0]["test_task_url"]


async def test_no_filter_ok(test_task_repo, vacancy_repo):
    v1_id = (
        await vacancy_repo.create_vacancy(VacancyCreate(title="V1", description="D2"))
    )["id"]
    v2_id = (
        await vacancy_repo.create_vacancy(VacancyCreate(title="V1", description="D2"))
    )["id"]

    await test_task_repo.create_test_task(
        TestTaskCreate(title="T1", test_task_url="https://github.com", vacancy_id=v1_id)
    )
    await test_task_repo.create_test_task(
        TestTaskCreate(title="T2", test_task_url="https://gitlab.com", vacancy_id=v2_id)
    )

    filters = TestTasksFilter()
    result = await test_task_repo.filter_test_tasks(filters)

    assert result["total"] == 2


async def test_patch_test_task(test_task_repo, vacancy_repo):
    vacancy_id = (
        await vacancy_repo.create_vacancy(
            VacancyCreate(title="Title1", description="desc")
        )
    )["id"]
    test_task = TestTaskCreate(
        title="Test title 1", test_task_url="https://google.com", vacancy_id=vacancy_id
    )
    test_task_id = (await test_task_repo.create_test_task(test_task))["id"]
    changed_test_task = {"title": "New title", "test_task_url": "https://yahoo.com"}
    got_test_task = await test_task_repo.patch_test_task(
        test_task_id, changed_test_task
    )
    assert got_test_task["id"] is not None
    assert got_test_task["title"] == changed_test_task["title"]
    assert got_test_task["vacancy_id"] == vacancy_id
    assert got_test_task["test_task_url"] == changed_test_task["test_task_url"]
