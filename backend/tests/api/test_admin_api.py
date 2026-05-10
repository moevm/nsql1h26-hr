async def test_backup(admin_client):
    response = await admin_client.get("/admin/backup")
    assert response.status_code == 200
