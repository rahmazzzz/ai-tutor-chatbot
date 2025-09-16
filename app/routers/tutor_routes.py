import logging
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.deps import get_current_user
from app.clients.supabase_client import get_db
from app.container.core_container import container  # global singleton container

# Configure logger
logger = logging.getLogger("tutor_routes")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

router = APIRouter(prefix="/tutor", tags=["Tutor"])

# Use services directly from container
file_processing_service = container.file_processing_service
embedding_service = container.embedding_service
storage_service = container.storage_service
rag_service = container.rag_service
summarize_video_service = container.summarize_video_service


class VideoLink(BaseModel):
    url: str


@router.post("/upload")
def upload_and_embed(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    logger.info(f"Uploading file '{file.filename}' for user {current_user['sub']}")
    file_bytes = file.file.read()
    file_path = f"{current_user['sub']}/{file.filename}"

    # Upload file to storage
    storage_service.upload_file(
        bucket="user-files",
        file_path=file_path,
        file_content=file_bytes,
        token=current_user.get("token")
    )
    logger.info(f"File '{file.filename}' uploaded successfully")

    # Extract and chunk text
    text = file_processing_service.extract_text_from_pdf(file_bytes)
    chunks = file_processing_service.chunk_text(text)
    logger.info(f"Extracted and chunked text into {len(chunks)} chunks")

    # Create embeddings
    embedding_service.create_and_store_embeddings(
        user_id=current_user["sub"],
        filename=file.filename,
        file_path=file_path,
        chunks=chunks
    )
    logger.info(f"Embeddings stored for file '{file.filename}'")

    return {"message": "File uploaded and embeddings stored", "num_chunks": len(chunks)}


@router.post("/ask")
def ask_question(
    question: str,
    current_user=Depends(get_current_user),
):
    logger.info(f"User {current_user['sub']} asking question: {question}")

    # Use RAG service from container
    answer = rag_service.chat(user_input=question, user_id=current_user['sub'])

    logger.info(f"Answer generated: {answer}")
    return {"answer": answer}


@router.post("/summarize_video")
def summarize_video(data: VideoLink, user=Depends(get_current_user)):
    summary = summarize_video_service(data.url)
    return {
        "url": data.url,
        "summary": summary
    }
