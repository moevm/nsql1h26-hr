import pytest
import uuid
from datetime import datetime, UTC
from app.models.user import UserCreate, Role
from app.models.offer import OfferStatus
from app.services.user_service import UserService
from app.repositories.user_repo import UserRepository


@pytest.fixture
async def user_repo(neo4j_driver):
    return UserRepository(neo4j_driver)


@pytest.fixture
async def user_service(user_repo):
    return UserService(user_repo)


async def test_patch_offer(hr_client, manager_client, user_service):
    hr = await user_service.create_user(
        UserCreate(
            email="hr@test.com",
            full_name="Hrrrrr",
            password="hash123456",
            role=Role.HR,
        )
    )
    hr_id = hr.id
    response = await hr_client.post(
        "/vacancies", json={"title": "Vacancy 1", "description": "Test Description"}
    )
    assert response.status_code == 201
    data = response.json()
    vacancy_id = data["id"]
    response = await hr_client.post(
        "/test-tasks",
        json={
            "title": "Test task 1",
            "test_task_url": "https://google.com/",
            "vacancy_id": str(vacancy_id),
        },
    )
    assert response.status_code == 201
    data = response.json()
    test_task_id = data["id"]
    full_name = "Candidate B"
    email = "candidate@email.com"
    phone = "+79638527474"
    resume_url = "https://google.com/"
    response = await hr_client.post(
        "/candidates",
        json={
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "status": "NEW",
            "vacancy_id": vacancy_id,
            "test_task_id": test_task_id,
            "resume_url": resume_url
        }
    )
    assert response.status_code == 201
    candidate_id = response.json()["id"]

    response = await hr_client.patch(
        f"/candidates/{candidate_id}",
        json={
            "status": "INTERVIEW_PASSED"
        }
    )

    response = await hr_client.post(
        "/offers",
        json={
            "candidate_id": str(candidate_id),
            "vacancy_id": str(vacancy_id),
            "created_by": str(hr_id),
            "salary": 100500,
            "start_at": int(datetime.now(UTC).timestamp())
        }
    )
    assert response.status_code == 201

    offer_id = response.json()["id"]
    response = await manager_client.patch(
        f"/offers/{offer_id}",
        json={
            "status": OfferStatus.APPROVED_CND
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == str(OfferStatus.APPROVED_CND)
