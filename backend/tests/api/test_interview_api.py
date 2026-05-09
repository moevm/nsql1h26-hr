import pytest
import uuid
from datetime import datetime, timedelta, timezone
from app.models.user import UserCreate, Role
from app.services.user_service import UserService
from app.repositories.user_repo import UserRepository


@pytest.fixture
async def user_repo(neo4j_driver):
    return UserRepository(neo4j_driver)


@pytest.fixture
async def user_service(user_repo):
    return UserService(user_repo)


@pytest.fixture
async def test_tech_spec(user_service):
    user = await user_service.create_user(
        UserCreate(
            email=f"tech_{uuid.uuid4()}@test.com",
            full_name="Test Tech Spec",
            password="hash123456",
            role=Role.TECH_SPEC
        )
    )
    return user


async def test_create_interview_ok(hr_client, user_service):
    tech_spec = await user_service.create_user(
        UserCreate(
            email="tech_api@test.com",
            full_name="Tech API",
            password="hash123456",
            role=Role.TECH_SPEC
        )
    )
    tech_spec_id = tech_spec.id

    vacancy_resp = await hr_client.post(
        "/vacancies", json={"title": "Interview Vacancy", "description": "For interview testing"}
    )
    assert vacancy_resp.status_code == 201
    vacancy_id = vacancy_resp.json()["id"]

    candidate_resp = await hr_client.post(
        "/candidates",
        json={
            "full_name": "Interview Candidate",
            "email": "interview@example.com",
            "phone": "+71234567890",
            "status": "NEW",
            "vacancy_id": vacancy_id,
            "resume_url": "https://example.com/resume.pdf"
        }
    )
    assert candidate_resp.status_code == 201
    candidate_id = candidate_resp.json()["id"]

    scheduled_at = datetime.now(timezone.utc) + timedelta(days=1)
    scheduled_at_iso = scheduled_at.isoformat()
    scheduled_at_timestamp = int(scheduled_at.timestamp())

    response = await hr_client.post(
        "/interviews",
        json={
            "candidate_id": candidate_id,
            "tech_spec_id": str(tech_spec_id),
            "scheduled_at": scheduled_at_iso,
            "zoom_url": "https://zoom.us/test",
            "result": "AWAIT_INTERVIEW"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["candidate_id"] == candidate_id
    assert data["tech_spec_id"] == str(tech_spec_id)
    assert data["scheduled_at"] == scheduled_at_timestamp
    assert data["zoom_url"] == "https://zoom.us/test"
    assert data["result"] == "AWAIT_INTERVIEW"
    assert data["feedback"] is None


async def test_create_interview_candidate_not_found(hr_client, user_service):
    tech_spec = await user_service.create_user(
        UserCreate(
            email="tech_api2@test.com",
            full_name="Tech API 2",
            password="hash123456",
            role=Role.TECH_SPEC
        )
    )
    tech_spec_id = tech_spec.id
    
    scheduled_at = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    non_existent_candidate_id = str(uuid.uuid4())

    response = await hr_client.post(
        "/interviews",
        json={
            "candidate_id": non_existent_candidate_id,
            "tech_spec_id": str(tech_spec_id),
            "scheduled_at": scheduled_at
        }
    )
    assert response.status_code == 400


async def test_get_interview_by_id_ok(hr_client, user_service):
    tech_spec = await user_service.create_user(
        UserCreate(
            email="tech_api3@test.com",
            full_name="Tech API 3",
            password="hash123456",
            role=Role.TECH_SPEC
        )
    )
    tech_spec_id = tech_spec.id
    
    vacancy_resp = await hr_client.post(
        "/vacancies", json={"title": "Get Interview Vacancy", "description": "Test"}
    )
    assert vacancy_resp.status_code == 201
    vacancy_id = vacancy_resp.json()["id"]

    candidate_resp = await hr_client.post(
        "/candidates",
        json={
            "full_name": "Get Candidate",
            "email": "get@example.com",
            "phone": "+71234567890",
            "status": "NEW",
            "vacancy_id": vacancy_id
        }
    )
    assert candidate_resp.status_code == 201
    candidate_id = candidate_resp.json()["id"]

    scheduled_at = datetime.now(timezone.utc) + timedelta(days=1)
    scheduled_at_iso = scheduled_at.isoformat()
    create_resp = await hr_client.post(
        "/interviews",
        json={
            "candidate_id": candidate_id,
            "tech_spec_id": str(tech_spec_id),
            "scheduled_at": scheduled_at_iso,
            "zoom_url": "https://zoom.us/get",
            "result": "AWAIT_INTERVIEW"
        }
    )
    assert create_resp.status_code == 201
    interview = create_resp.json()
    interview_id = interview["id"]

    response = await hr_client.get(f"/interviews/{interview_id}")
    assert response.status_code == 200
    got = response.json()
    assert got == interview


async def test_get_interview_by_id_not_found(hr_client):
    non_existent_id = str(uuid.uuid4())
    response = await hr_client.get(f"/interviews/{non_existent_id}")
    assert response.status_code == 404


async def test_filter_interviews_ok(hr_client, user_service):
    tech_spec_1 = await user_service.create_user(
        UserCreate(
            email="tech_f1@test.com",
            full_name="Tech Filter 1",
            password="hash123456",
            role=Role.TECH_SPEC
        )
    )
    tech_spec_2 = await user_service.create_user(
        UserCreate(
            email="tech_f2@test.com",
            full_name="Tech Filter 2",
            password="hash123456",
            role=Role.TECH_SPEC
        )
    )

    vacancy_resp = await hr_client.post(
        "/vacancies", json={"title": "Filter Vacancy", "description": "Test"}
    )
    assert vacancy_resp.status_code == 201
    vacancy_id = vacancy_resp.json()["id"]
    candidate_resp = await hr_client.post(
        "/candidates",
        json={
            "full_name": "Filter Candidate",
            "email": "filter@ex.com",
            "phone": "+71234567890",
            "status": "NEW",
            "vacancy_id": vacancy_id
        }
    )
    assert candidate_resp.status_code == 201
    candidate_id = candidate_resp.json()["id"]

    now = datetime.now(timezone.utc)
    await hr_client.post(
        "/interviews",
        json={
            "candidate_id": candidate_id,
            "tech_spec_id": str(tech_spec_1.id),
            "scheduled_at": (now + timedelta(days=1)).isoformat(),
            "result": "INTERVIEW_PASSED"
        }
    )
    await hr_client.post(
        "/interviews",
        json={
            "candidate_id": candidate_id,
            "tech_spec_id": str(tech_spec_2.id),
            "scheduled_at": (now + timedelta(days=2)).isoformat(),
            "result": "INTERVIEW_FAILED"
        }
    )

    # Фильтр без параметров
    response = await hr_client.get("/interviews")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2

    # Фильтр по результату — упадёт 
    response = await hr_client.get("/interviews", params={"result": "INTERVIEW_PASSED"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["result"] == "INTERVIEW_PASSED"


async def test_filter_interviews_by_date(hr_client, user_service):
    tech_spec = await user_service.create_user(
        UserCreate(
            email="tech_date@test.com",
            full_name="Tech Date",
            password="hash123456",
            role=Role.TECH_SPEC
        )
    )
    tech_spec_id = tech_spec.id
    
    vacancy_resp = await hr_client.post(
        "/vacancies", json={"title": "Date Filter Vacancy", "description": "Test"}
    )
    assert vacancy_resp.status_code == 201
    vacancy_id = vacancy_resp.json()["id"]
    candidate_resp = await hr_client.post(
        "/candidates",
        json={
            "full_name": "Date Candidate",
            "email": "date@ex.com",
            "phone": "+71234567890",
            "status": "NEW",
            "vacancy_id": vacancy_id
        }
    )
    assert candidate_resp.status_code == 201
    candidate_id = candidate_resp.json()["id"]

    now = datetime.now(timezone.utc)
    date_from = int((now + timedelta(days=1)).timestamp())
    date_to = int((now + timedelta(days=3)).timestamp())

    await hr_client.post(
        "/interviews",
        json={
            "candidate_id": candidate_id,
            "tech_spec_id": str(tech_spec_id),
            "scheduled_at": (now + timedelta(days=2)).isoformat()
        }
    )

    response = await hr_client.get(
        "/interviews",
        params={"scheduled_at_from": date_from, "scheduled_at_to": date_to}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1


async def test_create_interview_tech_spec_not_found(hr_client, user_service):
    """Ожидаем 400, если tech_spec не найден """
    
    vacancy_resp = await hr_client.post(
        "/vacancies", json={"title": "Date Filter Vacancy", "description": "Test"}
    )
    assert vacancy_resp.status_code == 201
    vacancy_id = vacancy_resp.json()["id"]
    candidate_resp = await hr_client.post(
        "/candidates",
        json={
            "full_name": "Date Candidate",
            "email": "date@ex.com",
            "phone": "+71234567890",
            "status": "NEW",
            "vacancy_id": vacancy_id
        }
    )
    assert candidate_resp.status_code == 201
    candidate_id = candidate_resp.json()["id"]

    non_existent_tech_spec_id = str(uuid.uuid4())
    scheduled_at_iso = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    response = await hr_client.post(
        "/interviews",
        json={
            "candidate_id": candidate_id,
            "tech_spec_id": non_existent_tech_spec_id,
            "scheduled_at": scheduled_at_iso
        }
    )
    assert response.status_code == 400


@pytest.mark.parametrize("missing_field", [
    "candidate_id",
    "tech_spec_id",
    "scheduled_at"
])
async def test_create_interview_missing_required_fields(hr_client, missing_field):
    """При отсутствии обязательного поля возвращается 422."""
    valid_data = {
        "candidate_id": str(uuid.uuid4()),
        "tech_spec_id": str(uuid.uuid4()),
        "scheduled_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    }
    # Удаляем проверяемое поле
    invalid_data = {k: v for k, v in valid_data.items() if k != missing_field}
    
    response = await hr_client.post("/interviews", json=invalid_data)
    assert response.status_code == 422


async def test_filter_interviews_api_invalid_date_range_returns_400(hr_client):
    """API должен возвращать 400 при некорректном диапазоне дат"""
    response = await hr_client.get(
        "/interviews",
        params={
            "scheduled_at_from": 2000,
            "scheduled_at_to": 1000
        }
    )
    assert response.status_code == 400
    assert "scheduled_at_from must be <= scheduled_at_to" in response.text