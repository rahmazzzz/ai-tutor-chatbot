# app/services/voice_service.py
# app/services/voice_service.py
from elevenlabs import ElevenLabs, Voice
from app.core.config import settings
import asyncio
import warnings
import io
import wave
import struct
import requests
import certifi


class VoiceService:
    def __init__(self):
        self.client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        self.voice_name = settings.VOICE_NAME
        self.voice: Voice | None = None

        if not settings.ELEVENLABS_API_KEY:
            raise ValueError(
                "[VoiceService] ELEVENLABS_API_KEY is missing! TTS/STT will not work."
            )

        try:
            response = self.client.voices.get_all()
            all_voices = getattr(response, "voices", [])

            if not all_voices:
                warnings.warn("[VoiceService] No voices found in your ElevenLabs account.")

            # Find the requested voice by name
            self.voice = next((v for v in all_voices if v.name == self.voice_name), None)

            # Fallback: first available voice
            if not self.voice and all_voices:
                self.voice = all_voices[0]
                warnings.warn(
                    f"[VoiceService] Desired voice '{self.voice_name}' not found. "
                    f"Using fallback voice '{self.voice.name}'."
                )

        except Exception as e:
            raise RuntimeError(
                f"[VoiceService] Failed to fetch voices. Check API key permissions. Error: {e}"
            ) from e

        print(f"[VoiceService] Initialized successfully with voice: {self.voice.name if self.voice else 'None'}")

    async def speak(self, text: str) -> bytes:
        """Generate speech from text asynchronously (TTS)."""
        if not self.voice:
            return self._silent_wav()

        loop = asyncio.get_event_loop()
        try:
            audio_bytes = await loop.run_in_executor(
                None, lambda: self.client.text_to_speech(self.voice.id, text)
            )
            return audio_bytes
        except Exception as e:
            warnings.warn(f"[VoiceService] TTS generation failed: {e}")
            return self._silent_wav()

    async def transcribe(self, audio_file: bytes) -> str:
        """STT using ElevenLabs REST API with SSL verification and valid model_id."""
        if not settings.ELEVENLABS_API_KEY:
            warnings.warn("[VoiceService] ELEVENLABS_API_KEY missing. Cannot perform STT.")
            return ""

        try:
            files = {"file": ("audio.wav", io.BytesIO(audio_file), "audio/wav")}
            data = {"model_id": "scribe_v1"}  # valid STT model

            response = await asyncio.to_thread(
                requests.post,
                "https://api.elevenlabs.io/v1/speech-to-text",
                headers={"xi-api-key": settings.ELEVENLABS_API_KEY},
                files=files,
                data=data,
                verify=certifi.where()  # ensures proper SSL certificate verification
            )

            if response.status_code == 200:
                return response.json().get("text", "")
            else:
                warnings.warn(f"[VoiceService] STT failed: {response.text}")
                return ""

        except Exception as e:
            warnings.warn(f"[VoiceService] STT request failed: {e}")
            return ""

    def _silent_wav(self) -> bytes:
        """Generate a 0.5s silent WAV as fallback."""
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(22050)
            frames = struct.pack('<' + 'h'*11025, *([0]*11025))
            wf.writeframes(frames)
        buffer.seek(0)
        return buffer.read()
