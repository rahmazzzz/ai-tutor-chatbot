from app.services.rag_service import RAGService

def test_rag_query():
    service = RAGService()
    question = "What is AI?"
    # Assume some documents are already stored
    answer = service.answer_question(question)
    assert isinstance(answer, str)
    assert len(answer) > 0
