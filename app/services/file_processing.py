# app/services/file_processing.py
import pdfplumber
from io import BytesIO
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.exceptions.base_exceptions import ValidationError, ExternalServiceError


class FileProcessingService:

    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        try:
            text = ""
            # Wrap bytes in BytesIO to make it file-like
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if not text.strip():
                raise ValidationError("PDF contains no extractable text.")
            return text
        except Exception as e:
            raise ExternalServiceError(f"Failed to extract text from PDF: {str(e)}")

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 50) -> list[str]:
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=overlap
            )
            chunks = splitter.split_text(text)
            if not chunks:
                raise ValidationError("Text could not be split into chunks.")
            return chunks
        except Exception as e:
            raise ExternalServiceError(f"Failed to chunk text: {str(e)}")
