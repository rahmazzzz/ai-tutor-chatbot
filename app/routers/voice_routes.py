# app/routers/voice_routes.py
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.agents.voice_agent import VoiceAgent
from app.clients.supabase_client import get_db
import base64

router = APIRouter(prefix="/voice", tags=["Voice Agent"])

@router.post("/process")
async def process_voice(
    file: UploadFile = File(...),
    user_id: str = "guest",
    db: Session = Depends(get_db)
):
    """
    Receives audio from the user, converts it to text,
    processes via chatbot/orchestrator, and returns
    both text and TTS audio (now using ElevenLabs).
    """
    # Read the uploaded audio bytes
    audio_bytes = await file.read()

    # Initialize VoiceAgent with DB session
    agent = VoiceAgent(db)

    # Process audio -> get response text and TTS audio
    result = await agent.handle_audio(audio_bytes, user_id)

    # Encode audio bytes to base64 for transport
    audio_base64 = base64.b64encode(result["audio"]).decode("utf-8")

    return {"text": result["text"], "audio": audio_base64}
