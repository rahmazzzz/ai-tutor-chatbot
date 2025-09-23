# app/services/tts_service.py
import aiohttp
from app.core.config import settings


class VoiceService:
    def __init__(self, voice_id: str = "pNInz6obpgDQGcFmaJgB"):  # Adam by default
        if not settings.ELEVENLABS_API_KEY:
            raise ValueError("❌ ELEVENLABS_API_KEY is missing in config.py")

        self.voice_id = voice_id
        self.api_url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"

    async def speak(self, text: str) -> bytes:
        """
        Convert text to speech using ElevenLabs API (async).
        Returns raw audio bytes instead of saving to file.
        """
        headers = {
            "xi-api-key": settings.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }

        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {"stability": 0.3, "similarity_boost": 0.8},
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    err = await resp.text()
                    print(f"[VoiceService] ❌ HTTP {resp.status}: {err}")
                    return b""
                return await resp.read()
