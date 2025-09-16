import pytest
from unittest.mock import MagicMock
from app.services.rag_service import RAGService
from app.container import core_container

# Fixture to mock RAGService globally
@pytest.fixture(autouse=True)
def mock_rag_service(monkeypatch):
    mock_service = MagicMock(spec=RAGService)
    # Patch the container's _service attribute
    monkeypatch.setattr(core_container.RAGContainer, "_service", mock_service)
    yield mock_service
