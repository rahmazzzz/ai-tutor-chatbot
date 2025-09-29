import tempfile
import wave
import numpy as np
from faster_whisper import WhisperModel

class STTService:
    def __init__(self, model_size="tiny", device="cpu"):
        self.model = WhisperModel(model_size, device=device, compute_type="int8")

    async def transcribe(self, audio_bytes: bytes) -> str:
        # Save incoming bytes to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            try:
                # Try to write as WAV first
                with wave.open(tmp.name, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(16000)
                    wf.writeframes(audio_bytes)
            except Exception:
                # If WAV writing fails, just write raw bytes
                tmp.write(audio_bytes)
                tmp.flush()

            try:
                segments, _ = self.model.transcribe(tmp.name)
                text = " ".join([seg.text for seg in segments])
                return text.strip()
            except Exception as e:
                print(f"[STTService] Transcription failed: {e}")
                return ""
