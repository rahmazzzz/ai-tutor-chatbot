from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_DB_URL: str

    # HuggingFace
    HF_API_TOKEN: str
    ELEVENLABS_API_KEY: str
    VOICE_NAME: str    # default voice
    ELEVENLABS_MODEL: str = "eleven_multilingual_v2"  # multilingual model
    GOOGLE_API_KEY: str

    # JWT
    JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Mistral + others
    MISTRAL_API_KEY: str
    TAVILY_API_KEY: str | None = None
    MISTRAL_MODEL: str = "magistral-medium-2507"
    MISTRAL_TEMPERATURE: float = 0.7
    GEMINI_API_KEY: str
    COHERE_API_KEY: str
    TTS_ENGINE: str = "gtts"

    # ✅ Pydantic v2 config
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def SUPABASE_JWKS_URL(self) -> str:
        return f"{self.SUPABASE_URL}/auth/v1/jwks"


settings = Settings()
