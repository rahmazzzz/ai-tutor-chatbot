# app/routers/tutor_routes.py
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.deps import get_current_user
from app.services.file_processing import FileProcessingService
from app.services.embedding_service import EmbeddingService
from app.services.storage_service import StorageService
from app.services.rag_service import RAGService
from app.clients.supabase_client import get_db  # <-- import here

router = APIRouter(prefix="/tutor", tags=["Tutor"])

file_processor = FileProcessingService()
embedding_service = EmbeddingService()
storage_service = StorageService()


@router.post("/upload")
def upload_and_embed(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),   # <-- inject db
    current_user=Depends(get_current_user),
):
    file_bytes = file.file.read()
    file_path = f"{current_user['sub']}/{file.filename}"

    storage_service.upload_file(
        bucket="user-files",
        file_path=file_path,
        file_content=file_bytes,
        token=current_user.get("token")
    )

    text = file_processor.extract_text_from_pdf(file_bytes)
    chunks = file_processor.chunk_text(text)

    embedding_service.create_and_store_embeddings(
        db=db,  # <-- use db session
        user_id=current_user["sub"],
        filename=file.filename,
        file_path=file_path,
        chunks=chunks
    )

    return {"message": "File uploaded and embeddings stored", "num_chunks": len(chunks)}


@router.post("/ask")
def ask_question(
    question: str,
    db: Session = Depends(get_db),   # <-- inject db
    current_user=Depends(get_current_user),
):
    rag_service = RAGService(db)  # <-- give db to RAGService
    answer = rag_service.ask_question(question=question)
    return {"answer": answer}
