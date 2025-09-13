from app.services.embedding_service import EmbeddingService

def test_embedding_generation():
    service = EmbeddingService()
    text = "Hello world"
    embedding_vector = service.create_embedding(text)
    assert isinstance(embedding_vector, list)
    assert len(embedding_vector) > 0
