import pytest
import uuid
from datetime import datetime


async def test_create_test_task_ok(async_client):
    response = await async_client.post(
        "/vacancies", json={"title": "Vacancy 1", "description": "Test Description"}
    )
    data = response.json()
    vacancy_id = data["id"]

    title = "Test task 1"
    test_task_url = "https://google.com/"

    response = await async_client.post(
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


async def test_create_test_task_bad_vacancy_id(async_client):
    response = await async_client.post(
        "/vacancies", json={"title": "Vacancy 1", "description": "Test Description"}
    )
    data = response.json()
    vacancy_id = uuid.uuid4()

    title = "Test task 1"
    test_task_url = "https://google.com/"

    response = await async_client.post(
        "/test-tasks",
        json={
            "title": title,
            "test_task_url": test_task_url,
            "vacancy_id": str(vacancy_id),
        },
    )
    assert response.status_code == 404


async def test_get_vacancy_by_id(async_client):
    response = await async_client.post(
        "/vacancies", json={"title": "Vacancy 1", "description": "Test Description"}
    )
    data = response.json()
    vacancy_id = data["id"]
    title = "Test task 1"
    test_task_url = "https://google.com/"
    response = await async_client.post(
        "/test-tasks",
        json={
            "title": title,
            "test_task_url": test_task_url,
            "vacancy_id": str(vacancy_id),
        },
    )
    test_task = response.json()
    test_task_id = test_task["id"]
    response = await async_client.get(f"/test-tasks/{test_task_id}")
    assert response.status_code == 200
    got_test_task = response.json()
    assert got_test_task == test_task


async def test_get_vacancy_bad_id(async_client):
    response = await async_client.post(
        "/vacancies", json={"title": "Vacancy 1", "description": "Test Description"}
    )
    data = response.json()
    vacancy_id = data["id"]
    title = "Test task 1"
    test_task_url = "https://google.com/"
    response = await async_client.post(
        "/test-tasks",
        json={
            "title": title,
            "test_task_url": test_task_url,
            "vacancy_id": str(vacancy_id),
        },
    )
    test_task_id = uuid.uuid4()
    response = await async_client.get(f"/test-tasks/{test_task_id}")
    assert response.status_code == 404
