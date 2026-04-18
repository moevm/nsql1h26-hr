import pytest
import uuid
from datetime import datetime


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


async def test_get_vacancy_by_id_bad_uuid(async_client):
    response = await async_client.get("/vacancies/bad-id")
    assert response.status_code == 422


async def test_patch_vacancy_ok(async_client):
    title = "Vacancy 1"
    description = "Test Description"
    response = await async_client.post(
        "/vacancies", json={"title": title, "description": description}
    )
    data = response.json()
    vacancy_id = str(data["id"])

    response = await async_client.patch(
        f"/vacancies/{vacancy_id}", json={"description": "Update",
                                          "status": "CLOSED"}
    )
    assert response.status_code == 200
    got_data = response.json()
    assert got_data["title"] == title
    assert got_data["description"] == "Update"
    assert got_data["status"] == "CLOSED"
    assert got_data["closed_at"] is not None


async def test_patch_vacancy_not_found(async_client):
    vacancy_id = str(uuid.uuid4())

    response = await async_client.patch(
        f"/vacancies/{vacancy_id}", json={"description": "Update",
                                          "status": "CLOSED"}
    )
    assert response.status_code == 404


async def test_patch_vacancy_invalid_params(async_client):
    title = "Vacancy 1"
    description = "Test Description"
    response = await async_client.post(
        "/vacancies", json={"title": title, "description": description}
    )
    data = response.json()
    vacancy_id = str(data["id"])

    response = await async_client.patch(
        f"/vacancies/{vacancy_id}", json={"closed_at": int(datetime.now().timestamp()),
                                          "status": "OPEN"}
    )
    assert response.status_code == 400


async def test_filter_vacancies_ok(async_client):
    v1_data = {"title": "Python Developer", "description": "Backend focus"}
    v2_data = {"title": "Frontend Developer", "description": "React focus"}
    
    resp1 = await async_client.post("/vacancies", json=v1_data)
    resp2 = await async_client.post("/vacancies", json=v2_data)
    
    vacancy1 = resp1.json()
    vacancy2 = resp2.json()

    # basic
    response = await async_client.get("/vacancies")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] >= 2
    item_ids = [item["id"] for item in data["items"]]
    assert vacancy1["id"] in item_ids
    assert vacancy2["id"] in item_ids

    # search in title
    response = await async_client.get("/vacancies", params={"title": "Python"})
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Python Developer"

    # sorting
    response = await async_client.get(
        "/vacancies", 
        params={"sort_by": "title", "sort_order": "desc"}
    )
    assert response.status_code == 200
    data = response.json()
    
    titles = [item["title"] for item in data["items"] if item["title"] in ["Python Developer", "Frontend Developer"]]
    assert titles == ["Python Developer", "Frontend Developer"]

async def test_filter_vacancies_empty_result(async_client):
    response = await async_client.get("/vacancies", params={"title": "NonExistentVacancyName"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []
