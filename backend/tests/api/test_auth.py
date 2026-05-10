async def test_register_and_login(auth_client):
    email = "testuser@example.com"
    name = "testuser"
    password = "very_strong_password123"
    role = "HR"
    response = await auth_client.post(
        "/auth/register",
        json={"email": email, "full_name": name, "role": role, "password": password},
    )
    assert response.status_code == 201
    response = await auth_client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
