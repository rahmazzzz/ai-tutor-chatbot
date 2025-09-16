# app/routers/tutor_routes.py
import logging
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.deps import get_current_user
from app.container.core_container import FileProcessingContainer, EmbeddingContainer, StorageContainer, RAGContainer
from app.clients.supabase_client import get_db  # <-- import here
from app.services.summarize_video import summarize_video_service
from pydantic import BaseModel
# Configure logger
logger = logging.getLogger("tutor_routes")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

router = APIRouter(prefix="/tutor", tags=["Tutor"])

# Initialize containers
file_processor_container = FileProcessingContainer()
embedding_container = EmbeddingContainer()
storage_container = StorageContainer()
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
    storage_container.service.upload_file(
        bucket="user-files",
        file_path=file_path,
        file_content=file_bytes,
        token=current_user.get("token")
    )
    logger.info(f"File '{file.filename}' uploaded successfully")

    # Extract and chunk text
    text = file_processor_container.service.extract_text_from_pdf(file_bytes)
    chunks = file_processor_container.service.chunk_text(text)
    logger.info(f"Extracted and chunked text into {len(chunks)} chunks")

    # Create embeddings
    embedding_container.service.create_and_store_embeddings(
        db=db,
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
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    logger.info(f"User {current_user['sub']} asking question: {question}")
    
    # Instantiate RAG service (via your container if you have one)
    rag_container = RAGContainer(db)
    
    # Use the new chat method which handles memory
    answer = rag_container.service.chat(user_input=question, user_id=current_user['sub'])
    
    logger.info(f"Answer generated: {answer}")
    return {"answer": answer}



@router.post("/summarize_video")
def summarize_video(data: VideoLink, user=Depends(get_current_user)):
    summary = summarize_video_service(data.url)
    return {
        "url": data.url,
        "summary": summary
    }