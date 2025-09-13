import pytest
from fastapi.testclient import TestClient
from app.utils.hashing import Hasher
from app.deps import create_access_token
from io import BytesIO

# -------------------------------
# Mock JWT Token Generator
# -------------------------------
def generate_test_token(email: str = "test@test.com") -> str:
    """
    Generate a test JWT token for a given email.
    """
    token = create_access_token(subject=email)
    return token

# -------------------------------
# Mock File Generator
# -------------------------------
def create_test_file(filename: str = "test.txt", content: bytes = b"Hello world"):
    """
    Returns a file-like object suitable for FastAPI file upload tests.
    """
    return {"file": (filename, BytesIO(content), "text/plain")}

# -------------------------------
# Password hashing helpers
# -------------------------------
def hash_password(password: str) -> str:
    """
    Hash a plain password (used for test DB setup).
    """
    return Hasher.get_password_hash(password)

# -------------------------------
# Example Pytest Fixtures
# -------------------------------
@pytest.fixture
def test_token():
    return generate_test_token()

@pytest.fixture
def test_file():
    return create_test_file()

@pytest.fixture
def hashed_password():
    return hash_password("password123")
