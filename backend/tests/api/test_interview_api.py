import uuid
from datetime import datetime, timedelta, timezone


async def test_create_interview_ok(hr_client, neo4j_driver):
    tech_spec_id = uuid.uuid4()

    async with neo4j_driver.session() as session:
        await session.run(
            """
            CREATE (u:User:TECH_SPEC {
                id: $id, email: $email, full_name: $full_name,
                password_hash: $hash, role: 'TECH_SPEC'
            })
            """,
            id=str(tech_spec_id), email="tech_api@test.com",
            full_name="Tech API", hash="hash"
        )

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


async def test_create_interview_candidate_not_found(hr_client, neo4j_driver):
    """БАГ: API возвращает 200 с None вместо 400, что вызывает ошибку валидации ответа."""
    tech_spec_id = uuid.uuid4()
    async with neo4j_driver.session() as session:
        await session.run(
            """
            CREATE (u:User:TECH_SPEC {
                id: $id, email: $email, full_name: $full_name,
                password_hash: $hash, role: 'TECH_SPEC'
            })
            """,
            id=str(tech_spec_id), email="tech_api2@test.com",
            full_name="Tech API 2", hash="hash"
        )
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


async def test_get_interview_by_id_ok(hr_client, neo4j_driver):
    tech_spec_id = uuid.uuid4()
    async with neo4j_driver.session() as session:
        await session.run(
            """
            CREATE (u:User:TECH_SPEC {
                id: $id, email: $email, full_name: $full_name,
                password_hash: $hash, role: 'TECH_SPEC'
            })
            """,
            id=str(tech_spec_id), email="tech_api3@test.com",
            full_name="Tech API 3", hash="hash"
        )
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
    """БАГ: API возвращает 200 с None вместо 404, что вызывает ошибку валидации ответа."""
    non_existent_id = str(uuid.uuid4())
    response = await hr_client.get(f"/interviews/{non_existent_id}")
    assert response.status_code == 404


async def test_filter_interviews_ok(hr_client, neo4j_driver):
    """БАГ: метод filter_interviews репозитория возвращает интервью с tech_spec_id=None,
    что приводит к ValidationError при сериализации ответа. Тест упадёт."""
    tech_spec_1 = uuid.uuid4()
    tech_spec_2 = uuid.uuid4()
    async with neo4j_driver.session() as session:
        for ts_id, email in [(tech_spec_1, "tech_f1@test.com"), (tech_spec_2, "tech_f2@test.com")]:
            await session.run(
                """
                CREATE (u:User:TECH_SPEC {
                    id: $id, email: $email, full_name: $full_name,
                    password_hash: $hash, role: 'TECH_SPEC'
                })
                """,
                id=str(ts_id), email=email, full_name="Tech Filter", hash="hash"
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
            "tech_spec_id": str(tech_spec_1),
            "scheduled_at": (now + timedelta(days=1)).isoformat(),
            "result": "INTERVIEW_PASSED"
        }
    )
    await hr_client.post(
        "/interviews",
        json={
            "candidate_id": candidate_id,
            "tech_spec_id": str(tech_spec_2),
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


async def test_filter_interviews_by_date(hr_client, neo4j_driver):
    tech_spec_id = uuid.uuid4()
    async with neo4j_driver.session() as session:
        await session.run(
            """
            CREATE (u:User:TECH_SPEC {
                id: $id, email: $email, full_name: $full_name,
                password_hash: $hash, role: 'TECH_SPEC'
            })
            """,
            id=str(tech_spec_id), email="tech_date@test.com",
            full_name="Tech Date", hash="hash"
        )
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
    date_from = (now + timedelta(days=1)).timestamp()
    date_to = (now + timedelta(days=3)).timestamp()

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