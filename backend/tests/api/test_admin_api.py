async def test_backup(admin_client):
    response = await admin_client.get("/admin/backup")
    assert response.status_code == 200


async def test_restore(admin_client):
    response = await admin_client.post(
        "/admin/restore",
        json={
            "users": [],
            "vacancies": [],
            "test_tasks": [],
            "candidates": [],
            "interviews": [],
            "offers": [],
        },
    )
    assert response.status_code == 200
