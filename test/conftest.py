# test/conftest.py
import pytest
from unittest.mock import MagicMock
from app.services.rag_service import RAGService

@pytest.fixture(autouse=True)
def mock_rag_service(monkeypatch):
    mock_chain = MagicMock()
    mock_chain.run.return_value = "Mocked answer"
    monkeypatch.setattr(RAGService, "rag_chain", mock_chain)
