import pytest


async def test_create_user(async_client):
    title = "Vacancy 1"
    description = "Test Description"
    response = await async_client.post(
        "/vacancies", json={"title": title, "description": description}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == title
    assert data["description"] == description
    assert data["status"] == "OPEN"
    assert data["created_at"] is not None
