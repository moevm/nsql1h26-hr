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


async def test_get_vacancy_by_id_ok(async_client):
    title = "Vacancy 1"
    description = "Test Description"
    response = await async_client.post(
        "/vacancies", json={"title": title, "description": description}
    )
    assert response.status_code == 201
    data = response.json()
    vacancy_id = str(data["id"])

    response = await async_client.get(f"/vacancies/{vacancy_id}")
    assert response.status_code == 200
    got_data = response.json()
    assert got_data == data


async def test_get_vacancy_by_id_bas_uuid(async_client):
    response = await async_client.get("/vacancies/bad-id")
    assert response.status_code == 422
