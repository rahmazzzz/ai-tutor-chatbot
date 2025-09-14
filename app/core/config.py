from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_DB_URL: str

    # HuggingFace
    HF_API_TOKEN: str

    # JWT
    JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MISTRAL_API_KEY: str
    TAVILY_API_KEY: str = None
    MISTRAL_MODEL: str = "magistral-medium-2507"
    MISTRAL_TEMPERATURE: float = 0.7 
    class Config:
        from_attributes = True
        env_file = ".env"

    @property
    def SUPABASE_JWKS_URL(self) -> str:
        return f"{self.SUPABASE_URL}/auth/v1/jwks"


settings = Settings()
