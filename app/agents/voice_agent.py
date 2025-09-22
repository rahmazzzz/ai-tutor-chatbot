# app/agents/voice_agent.py
from app.services.stt_service import STTService
from app.services.tts_service import VoiceService  # Async ElevenLabs TTS
from app.graph.langgraph_chatbot import ChatbotGraph
from sqlalchemy.orm import Session


class VoiceAgent:
    def __init__(self, db: Session):
        self.stt = STTService()
        self.tts = VoiceService()  # Async TTS service
        self.orchestrator = ChatbotGraph(db).build()

    async def handle_audio(self, audio_bytes: bytes, user_id: str = None) -> dict:
        user_id = user_id or "guest"
        print(f"[VoiceAgent] Handling audio for user_id={user_id}, audio size={len(audio_bytes)} bytes")

        # Step 1: Speech to Text
        text = await self.stt.transcribe(audio_bytes)
        print(f"[VoiceAgent] Transcribed text: {text}")

        if not text or not text.strip():
            fallback_response = "I couldn’t hear anything. Please try again."
            audio_out = await self._safe_speak(fallback_response)
            return {"text": fallback_response, "audio": audio_out}

        # Step 2: Orchestrator decides the agent and response
        try:
            result = await self.orchestrator.ainvoke({"message": text, "user_id": user_id})
            response_text = result.get("response", "Sorry, I couldn’t process that.")
        except Exception as e:
            print(f"[VoiceAgent] Orchestrator error: {e}")
            response_text = "Something went wrong while processing your request."

        print(f"[VoiceAgent] Orchestrator response: {response_text}")

        # Step 3: Convert response to speech (TTS)
        audio_out = await self._safe_speak(response_text)
        print(f"[VoiceAgent] Generated TTS audio (length={len(audio_out)} bytes)")

        return {"text": response_text, "audio": audio_out}

    async def _safe_speak(self, text: str) -> bytes:
        """
        Wrap TTS call with try/except to prevent crashes.
        Always returns bytes (may be empty if TTS fails).
        """
        try:
            audio = await self.tts.speak(text)  #  async TTS
            return audio or b""
        except Exception as e:
            print(f"[VoiceAgent] TTS failed: {e}")
            return b""
