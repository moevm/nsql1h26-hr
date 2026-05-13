import pytest
import uuid
from datetime import datetime


async def test_create_test_task_ok(hr_client):
    response = await hr_client.post(
        "/vacancies", json={"title": "Vacancy 1", "description": "Test Description"}
    )
    data = response.json()
    vacancy_id = data["id"]

    title = "Test task 1"
    test_task_url = "https://google.com/"

    response = await hr_client.post(
        "/test-tasks",
        json={
            "title": title,
            "test_task_url": test_task_url,
            "vacancy_id": str(vacancy_id),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == title
    assert data["test_task_url"] == test_task_url
    assert data["vacancy_id"] == str(vacancy_id)


async def test_create_test_task_bad_vacancy_id(hr_client):
    response = await hr_client.post(
        "/vacancies", json={"title": "Vacancy 1", "description": "Test Description"}
    )
    vacancy_id = uuid.uuid4()

    title = "Test task 1"
    test_task_url = "https://google.com/"

    response = await hr_client.post(
        "/test-tasks",
        json={
            "title": title,
            "test_task_url": test_task_url,
            "vacancy_id": str(vacancy_id),
        },
    )
    assert response.status_code == 404


async def test_get_vacancy_by_id(hr_client):
    response = await hr_client.post(
        "/vacancies", json={"title": "Vacancy 1", "description": "Test Description"}
    )
    data = response.json()
    vacancy_id = data["id"]
    title = "Test task 1"
    test_task_url = "https://google.com/"
    response = await hr_client.post(
        "/test-tasks",
        json={
            "title": title,
            "test_task_url": test_task_url,
            "vacancy_id": str(vacancy_id),
        },
    )
    test_task = response.json()
    test_task_id = test_task["id"]
    response = await hr_client.get(f"/test-tasks/{test_task_id}")
    assert response.status_code == 200
    got_test_task = response.json()
    assert got_test_task == test_task


async def test_get_vacancy_bad_id(hr_client):
    response = await hr_client.post(
        "/vacancies", json={"title": "Vacancy 1", "description": "Test Description"}
    )
    data = response.json()
    vacancy_id = data["id"]
    title = "Test task 1"
    test_task_url = "https://google.com/"
    response = await hr_client.post(
        "/test-tasks",
        json={
            "title": title,
            "test_task_url": test_task_url,
            "vacancy_id": str(vacancy_id),
        },
    )
    test_task_id = uuid.uuid4()
    response = await hr_client.get(f"/test-tasks/{test_task_id}")
    assert response.status_code == 404


async def test_filter_test_tasks(hr_client):
    vacancy_response = await hr_client.post(
        "/vacancies",
        json={"title": "Vacancy for test tasks", "description": "Filter test vacancy"},
    )
    vacancy = vacancy_response.json()
    vacancy_id = vacancy["id"]

    tasks_to_create = [
        {
            "title": "Test task 1",
            "test_task_url": "https://example.com/1",
            "vacancy_id": vacancy_id,
        },
        {
            "title": "Test task 2",
            "test_task_url": "https://example.com/2",
            "vacancy_id": vacancy_id,
        },
    ]
    created_tasks = []
    for task_data in tasks_to_create:
        resp = await hr_client.post("/test-tasks", json=task_data)
        created_tasks.append(resp.json())

    filter_response = await hr_client.get("/test-tasks")
    assert filter_response.status_code == 200
    result = filter_response.json()

    assert result["total"] == len(tasks_to_create)

    expected_sorted = sorted(created_tasks, key=lambda x: x["title"], reverse=False)
    assert result["items"] == expected_sorted


async def test_filter_by_vacancy_id_api(hr_client):
    vacancy1_resp = await hr_client.post(
        "/vacancies", json={"title": "V1", "description": "D1"}
    )
    assert vacancy1_resp.status_code == 201
    vacancy1 = vacancy1_resp.json()
    v1_id = vacancy1["id"]

    vacancy2_resp = await hr_client.post(
        "/vacancies", json={"title": "V2", "description": "D2"}
    )
    assert vacancy2_resp.status_code == 201
    vacancy2 = vacancy2_resp.json()
    v2_id = vacancy2["id"]

    task1_resp = await hr_client.post(
        "/test-tasks",
        json={
            "title": "T1",
            "test_task_url": "http://1.com",
            "vacancy_id": v1_id,
        },
    )
    assert task1_resp.status_code == 201

    task2_resp = await hr_client.post(
        "/test-tasks",
        json={
            "title": "T2",
            "test_task_url": "http://2.com",
            "vacancy_id": v2_id,
        },
    )
    assert task2_resp.status_code == 201

    filter_response = await hr_client.get(f"/test-tasks?vacancy_id={v1_id}")
    assert filter_response.status_code == 200
    result = filter_response.json()

    assert result["total"] == 1
    assert result["items"][0]["vacancy_id"] == v1_id
    assert result["items"][0]["title"] == "T1"


async def test_filter_by_title_substring_api(hr_client):
    vacancy1_resp = await hr_client.post(
        "/vacancies", json={"title": "V1", "description": "D1"}
    )
    assert vacancy1_resp.status_code == 201
    v1_id = vacancy1_resp.json()["id"]

    vacancy2_resp = await hr_client.post(
        "/vacancies", json={"title": "V2", "description": "D2"}
    )
    assert vacancy2_resp.status_code == 201
    v2_id = vacancy2_resp.json()["id"]

    task1_resp = await hr_client.post(
        "/test-tasks",
        json={
            "title": "Python Developer",
            "test_task_url": "http://1.com",
            "vacancy_id": v1_id,
        },
    )
    task1 = task1_resp.json()

    await hr_client.post(
        "/test-tasks",
        json={
            "title": "Frontend Lead",
            "test_task_url": "http://2.com",
            "vacancy_id": v2_id,
        },
    )

    filter_response = await hr_client.get("/test-tasks?title=DEV")
    assert filter_response.status_code == 200
    result = filter_response.json()

    assert result["total"] == 1
    assert "Python Developer" in result["items"][0]["title"]
    assert result["items"][0]["id"] == task1["id"]


async def test_patch_test_task(hr_client):
    response = await hr_client.post(
        "/vacancies", json={"title": "Vacancy 1", "description": "Test Description"}
    )
    data = response.json()
    vacancy_id = data["id"]

    response = await hr_client.post(
        "/test-tasks",
        json={
            "title": "old",
            "test_task_url": "https://old.com",
            "vacancy_id": str(vacancy_id),
        },
    )

    test_task = response.json()

    title = "Test new"
    test_task_url = "https://2gis.com/"

    response = await hr_client.patch(
        f"/test-tasks/{test_task["id"]}",
        json={
            "title": title,
            "test_task_url": test_task_url,
        },
    )
    data = response.json()
    assert response.status_code == 200
    assert data["title"] == title
    assert data["test_task_url"] == test_task_url
    assert data["vacancy_id"] == str(vacancy_id)
