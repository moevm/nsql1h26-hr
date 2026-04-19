
async def test_create_candidate(async_client):
    response = await async_client.post(
        "/vacancies", json={"title": "Vacancy 1", "description": "Test Description"}
    )
    data = response.json()
    vacancy_id = data["id"]
    response = await async_client.post(
        "/test-tasks",
        json={
            "title": "Test task 1",
            "test_task_url": "https://google.com/",
            "vacancy_id": str(vacancy_id),
        },
    )
    data = response.json()
    test_task_id = data["id"]
    full_name = "Candidate B"
    email = "candidate@email.com"
    phone = "+79638527474"
    resume_url = "https://google.com/"
    response = await async_client.post(
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

    data = response.json()
    assert data["id"] is not None
    assert data["full_name"] == full_name
    assert data["email"] == email
    assert data["phone"] == "tel:+7-963-852-74-74"
    assert data["status"] == "NEW"
    assert data["vacancy_id"] == vacancy_id
    assert data["test_task_id"] == test_task_id
    assert data["resume_url"] == resume_url
