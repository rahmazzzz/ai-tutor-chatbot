# test/test_auth_routes_simple.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)

# -----------------------------
# Patch AuthContainer methods only
# -----------------------------
@pytest.fixture(autouse=True)
def mock_auth_container():
    with patch("app.container.core_container.AuthContainer.register_user", new_callable=AsyncMock) as mock_register, \
         patch("app.container.core_container.AuthContainer.login_user", new_callable=AsyncMock) as mock_login:
        yield mock_register, mock_login


# -----------------------------
# Test register endpoint
# -----------------------------
def test_register_success(mock_auth_container):
    mock_register, _ = mock_auth_container
    mock_register.return_value = {"id": "user123", "email": "test@example.com"}

    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "strongpassword"}
    )

    assert response.status_code == 200
    assert response.json() == {"id": "user123", "email": "test@example.com"}
    mock_register.assert_awaited_once_with(email="test@example.com", password="strongpassword", username=None)


# -----------------------------
# Test login endpoint
# -----------------------------
def test_login_success(mock_auth_container):
    _, mock_login = mock_auth_container
    mock_login.return_value = {
        "access_token": "fake-token",
        "refresh_token": "fake-refresh",
        "user": {"id": "user123", "email": "test@example.com", "username": None}
    }

    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "strongpassword"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "fake-token",
        "refresh_token": "fake-refresh",
        "user": {"id": "user123", "email": "test@example.com", "username": None}
    }
    mock_login.assert_awaited_once_with(email="test@example.com", password="strongpassword")
