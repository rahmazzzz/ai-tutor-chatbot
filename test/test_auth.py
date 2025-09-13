def test_register(client, db_session):
    response = client.post(
        "/auth/register",
        json={"username": "testuser", "email": "test@test.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data

def test_login(client, db_session):
    response = client.post(
        "/auth/login",
        data={"username": "test@test.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
