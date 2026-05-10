
import pytest
import uuid
from datetime import datetime, UTC
from app.models.user import UserCreate, Role
from app.models.offer import OfferStatus
from app.models.candidate import CandidateStatus


async def _create_hr_user(user_service):
    return await user_service.create_user(
        UserCreate(
            email=f"hr_{uuid.uuid4()}@test.com",
            full_name="Test HR",
            password="hash123456",
            role=Role.HR,
        )
    )


async def _create_vacancy(hr_client):
    resp = await hr_client.post("/vacancies", json={
        "title": "Vacancy for Offer",
        "description": "Test description"
    })
    assert resp.status_code == 201
    return resp.json()


async def _create_candidate_interview_passed(hr_client, vacancy_id):
    # Создаём кандидата
    resp = await hr_client.post("/candidates", json={
        "full_name": "Candidate for Offer",
        "email": f"candidate_{uuid.uuid4()}@test.com",
        "phone": "+71234567890",
        "status": CandidateStatus.NEW,
        "vacancy_id": vacancy_id,
    })
    assert resp.status_code == 201
    candidate = resp.json()
    # Переводим в INTERVIEW_PASSED
    resp = await hr_client.patch(f"/candidates/{candidate['id']}", json={"status": CandidateStatus.INTERVIEW_PASSED})
    assert resp.status_code == 200
    candidate["status"] = CandidateStatus.INTERVIEW_PASSED
    return candidate


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
            "resume_url": resume_url,
        },
    )
    assert response.status_code == 201
    candidate_id = response.json()["id"]

    response = await hr_client.patch(
        f"/candidates/{candidate_id}", json={"status": "INTERVIEW_PASSED"}
    )

    response = await hr_client.post(
        "/offers",
        json={
            "candidate_id": str(candidate_id),
            "vacancy_id": str(vacancy_id),
            "created_by": str(hr_id),
            "salary": 100500,
            "start_at": int(datetime.now(UTC).timestamp()),
        },
    )
    assert response.status_code == 201

    offer_id = response.json()["id"]
    response = await manager_client.patch(
        f"/offers/{offer_id}", json={"status": OfferStatus.APPROVED_CND}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == str(OfferStatus.APPROVED_CND)


# === Тесты создания оффера ===
async def test_create_offer_ok(hr_client, user_service):
    hr_user = await _create_hr_user(user_service)
    vacancy = await _create_vacancy(hr_client)
    candidate = await _create_candidate_interview_passed(hr_client, vacancy["id"])

    payload = {
        "candidate_id": candidate["id"],
        "vacancy_id": vacancy["id"],
        "created_by": str(hr_user.id),
        "salary": 120000,
        "start_at": int(datetime.now(UTC).timestamp()) + 86400 * 30,
    }
    resp = await hr_client.post("/offers", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] is not None
    assert data["status"] == OfferStatus.PENDING


async def test_create_offer_candidate_not_found(hr_client, user_service):
    hr_user = await _create_hr_user(user_service)
    vacancy = await _create_vacancy(hr_client)

    payload = {
        "candidate_id": str(uuid.uuid4()),
        "vacancy_id": vacancy["id"],
        "created_by": str(hr_user.id),
        "salary": 100000,
        "start_at": int(datetime.now(UTC).timestamp()) + 86400,
    }
    resp = await hr_client.post("/offers", json=payload)
    assert resp.status_code == 400
    assert "Candidate not found" in resp.text


async def test_create_offer_vacancy_not_found(hr_client, user_service):
    hr_user = await _create_hr_user(user_service)
    vacancy = await _create_vacancy(hr_client)
    candidate = await _create_candidate_interview_passed(hr_client, vacancy["id"])

    payload = {
        "candidate_id": candidate["id"],
        "vacancy_id": str(uuid.uuid4()),
        "created_by": str(hr_user.id),
        "salary": 100000,
        "start_at": int(datetime.now(UTC).timestamp()) + 86400,
    }
    resp = await hr_client.post("/offers", json=payload)
    assert resp.status_code == 400
    assert "Vacancy not found" in resp.text


async def test_create_offer_wrong_candidate_status(hr_client, user_service):
    hr_user = await _create_hr_user(user_service)
    vacancy = await _create_vacancy(hr_client)

    # Создаём кандидата со статусом NEW
    resp = await hr_client.post("/candidates", json={
        "full_name": "Wrong Status Candidate",
        "email": f"wrong_{uuid.uuid4()}@test.com",
        "phone": "+71234567890",
        "status": CandidateStatus.NEW,
        "vacancy_id": vacancy["id"],
    })
    assert resp.status_code == 201
    candidate_id = resp.json()["id"]

    payload = {
        "candidate_id": candidate_id,
        "vacancy_id": vacancy["id"],
        "created_by": str(hr_user.id),
        "salary": 100000,
        "start_at": int(datetime.now(UTC).timestamp()) + 86400,
    }
    resp = await hr_client.post("/offers", json=payload)
    assert resp.status_code == 400
    assert "INTERVIEW_PASSED" in resp.text


async def test_create_offer_status_not_pending(hr_client, user_service):
    hr_user = await _create_hr_user(user_service)
    vacancy = await _create_vacancy(hr_client)
    candidate = await _create_candidate_interview_passed(hr_client, vacancy["id"])

    payload = {
        "candidate_id": candidate["id"],
        "vacancy_id": vacancy["id"],
        "created_by": str(hr_user.id),
        "salary": 100000,
        "start_at": int(datetime.now(UTC).timestamp()) + 86400,
        "status": OfferStatus.APPROVED_MNG
    }
    resp = await hr_client.post("/offers", json=payload)
    assert resp.status_code == 400


async def test_create_offer_unauthorized(async_client):
    payload = {
        "candidate_id": str(uuid.uuid4()),
        "vacancy_id": str(uuid.uuid4()),
        "created_by": str(uuid.uuid4()),
        "salary": 100000,
        "start_at": int(datetime.now(UTC).timestamp()) + 86400,
    }
    resp = await async_client.post("/offers", json=payload)
    assert resp.status_code == 401


async def test_create_offer_forbidden_for_tech_spec(tech_spec_client):
    # Проверка доступа: tech_spec не может создавать офферы
    payload = {
        "candidate_id": str(uuid.uuid4()),
        "vacancy_id": str(uuid.uuid4()),
        "created_by": str(uuid.uuid4()),
        "salary": 100000,
        "start_at": int(datetime.now(UTC).timestamp()) + 86400,
    }
    resp = await tech_spec_client.post("/offers", json=payload)
    assert resp.status_code == 403


# === Тесты получения оффера  ===
async def test_get_offer_by_id_ok(hr_client, user_service):
    hr_user = await _create_hr_user(user_service)
    vacancy = await _create_vacancy(hr_client)
    candidate = await _create_candidate_interview_passed(hr_client, vacancy["id"])

    create_resp = await hr_client.post("/offers", json={
        "candidate_id": candidate["id"],
        "vacancy_id": vacancy["id"],
        "created_by": str(hr_user.id),
        "salary": 100000,
        "start_at": int(datetime.now(UTC).timestamp()) + 86400,
    })
    assert create_resp.status_code == 201
    offer_id = create_resp.json()["id"]

    resp = await hr_client.get(f"/offers/{offer_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == offer_id


async def test_get_offer_by_id_not_found(hr_client):
    resp = await hr_client.get(f"/offers/{uuid.uuid4()}")
    assert resp.status_code == 404


async def test_get_offer_by_id_invalid_uuid(hr_client):
    resp = await hr_client.get("/offers/not-a-uuid")
    assert resp.status_code == 422


# === Тесты фильтрации офферов  ===
async def test_filter_offers_empty(hr_client):
    resp = await hr_client.get("/offers", params={"candidate_id": str(uuid.uuid4())})
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


async def test_filter_offers_basic(hr_client, user_service):
    hr_user = await _create_hr_user(user_service)
    vacancy = await _create_vacancy(hr_client)
    candidate = await _create_candidate_interview_passed(hr_client, vacancy["id"])

    create_resp = await hr_client.post("/offers", json={
        "candidate_id": candidate["id"],
        "vacancy_id": vacancy["id"],
        "created_by": str(hr_user.id),
        "salary": 100000,
        "start_at": int(datetime.now(UTC).timestamp()) + 86400,
    })
    assert create_resp.status_code == 201
    created = create_resp.json()

    resp = await hr_client.get("/offers")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert any(o["id"] == created["id"] for o in data["items"])

    resp = await hr_client.get("/offers", params={"candidate_id": candidate["id"]})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert all(o["candidate_id"] == candidate["id"] for o in data["items"])

async def test_filter_offers_pagination(hr_client, user_service):
    hr_user = await _create_hr_user(user_service)
    vacancy = await _create_vacancy(hr_client)
    base_start = int(datetime.now(UTC).timestamp()) + 86400

    # Создаём трёх разных кандидатов, чтобы обойти возможное ограничение на один оффер на кандидата
    for i in range(3):
        candidate = await _create_candidate_interview_passed(hr_client, vacancy["id"])
        await hr_client.post("/offers", json={
            "candidate_id": candidate["id"],
            "vacancy_id": vacancy["id"],
            "created_by": str(hr_user.id),
            "salary": 100000 + i * 10000,
            "start_at": base_start + i * 86400,
        })

    resp = await hr_client.get("/offers", params={"limit": 2, "offset": 0, "sort_by": "salary", "sort_order": "asc"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2


# === чутка на патч===

async def test_patch_offer_not_found(manager_client):
    resp = await manager_client.patch(f"/offers/{uuid.uuid4()}", json={"status": OfferStatus.APPROVED_MNG})
    assert resp.status_code == 404


async def test_patch_offer_forbidden_for_hr(hr_client, user_service):
    hr_user = await _create_hr_user(user_service)
    vacancy = await _create_vacancy(hr_client)
    candidate = await _create_candidate_interview_passed(hr_client, vacancy["id"])

    create_resp = await hr_client.post("/offers", json={
        "candidate_id": candidate["id"],
        "vacancy_id": vacancy["id"],
        "created_by": str(hr_user.id),
        "salary": 100000,
        "start_at": int(datetime.now(UTC).timestamp()) + 86400,
    })
    assert create_resp.status_code == 201
    offer_id = create_resp.json()["id"]

    resp = await hr_client.patch(f"/offers/{offer_id}", json={"status": OfferStatus.APPROVED_MNG})
    assert resp.status_code == 403