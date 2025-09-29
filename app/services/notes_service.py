# app/services/notes_service.py
from typing import List, Tuple
from app.services.rag_service import RAGService
from app.services.voice_service import VoiceService
import re
import asyncio
import warnings
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # or DEBUG for more detail

class NotesService:
    def __init__(self, db=None):
        self.rag_service = RAGService(db)
        self.voice_service = VoiceService()

    def clean_transcript(self, transcript: str) -> str:
        text = transcript.strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def make_notes(self, transcript: str) -> List[str]:
        cleaned = self.clean_transcript(transcript)
        if not cleaned:
            return ["- ⚠️ No transcript available."]
        try:
            summary = self.rag_service.summarize_text(cleaned)
            return [f"- {line}" for line in summary.split("\n") if line.strip()]
        except Exception:
            sentences = re.split(r"[.!?]", cleaned)
            return [f"- {s.strip()}" for s in sentences if s.strip()] or ["- ⚠️ Could not generate notes."]

    async def generate_from_audio(self, file) -> Tuple[str, List[str]]:
        audio_bytes = await file.read()

        try:
            transcript = await self.voice_service.transcribe(audio_bytes)
        except Exception as e:
            warnings.warn(f"[NotesService] Voice transcription failed: {e}")
            transcript = ""

        notes = self.make_notes(transcript)
        logger.info(f"[NotesService] Generated notes: {notes}")

        # Do NOT save automatically; manual save only
        return transcript, notes
