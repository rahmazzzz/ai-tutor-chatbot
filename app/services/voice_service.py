# app/services/voice_service.py
from elevenlabs import ElevenLabs, Voice
from app.core.config import settings
import asyncio
import warnings
import sys

class VoiceService:
    def __init__(self):
        # Initialize ElevenLabs client
        self.client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        self.voice_name = settings.VOICE_NAME
        self.voice: Voice = None

        # Validate API key early
        if not settings.ELEVENLABS_API_KEY:
            raise ValueError(
                "[VoiceService] ELEVENLABS_API_KEY is missing! TTS will not work."
            )

        try:
            all_voices = self.client.voices.get_all()  # requires voices_read permission
            if not all_voices:
                warnings.warn(
                    "[VoiceService] No voices found in your ElevenLabs account. TTS will fallback to silent audio."
                )
            
            # Try to find the requested voice
            self.voice = next((v for v in all_voices if v.name == self.voice_name), None)

            # Fallback: use first available voice if desired voice not found
            if not self.voice and all_voices:
                self.voice = all_voices[0]
                warnings.warn(
                    f"[VoiceService] Desired voice '{self.voice_name}' not found. Using fallback voice '{self.voice.name}'."
                )

            # Still no voice available
            if not self.voice:
                warnings.warn(
                    "[VoiceService] No usable voices available. TTS will return silent audio."
                )

        except Exception as e:
            raise RuntimeError(
                f"[VoiceService] Failed to fetch voices. Check API key permissions ('voices_read'). Error: {e}"
            ) from e

        print(f"[VoiceService] Initialized successfully with voice: {self.voice.name if self.voice else 'None'}")

    async def speak(self, text: str) -> bytes:
        """
        Generate speech from text asynchronously.
        Returns raw audio bytes (WAV). If TTS fails, returns a short silent WAV fallback.
        """
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

    def _silent_wav(self) -> bytes:
        """
        Returns a 0.5 second silent WAV byte array.
        """
        import wave
        import io
        import struct

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(1)       # mono
            wf.setsampwidth(2)       # 16-bit
            wf.setframerate(22050)   # sample rate
            frames = struct.pack('<' + 'h'*11025, *([0]*11025))  # 0.5s of silence
            wf.writeframes(frames)
        buffer.seek(0)
        return buffer.read()
