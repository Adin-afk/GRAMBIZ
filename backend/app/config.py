"""
Central application configuration.

All values are sourced from environment variables (see backend/.env.example).
No secrets are hard-coded here.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str = "development"
    DEMO_MODE: bool = True

    DATABASE_URL: str = (
        "postgresql+psycopg2://solapur_user:solapur_pass@localhost:5432/solapur_rural_db"
    )

    JWT_SECRET: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    GOOGLE_MAPS_API_KEY: str | None = None

    # Optional AI services. The application must remain fully functional
    # (financial engine, GIS, deterministic scoring) when these are unset.
    LLM_API_KEY: str | None = None
    LLM_MODEL: str | None = None
    EMBEDDING_MODEL: str | None = None

    # Google Gemini (used for the optional SWOT / plain-language explanation
    # layer in app/ai/gemini_service.py). Leave GEMINI_API_KEY unset to run
    # with this feature disabled; nothing else in the app depends on it.
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # ElevenLabs (optional "read aloud" text-to-speech layer, app/ai/elevenlabs_service.py).
    # The multilingual model natively covers most major Indian languages
    # (Hindi, Marathi, Bengali, Gujarati, Kannada, Malayalam, Tamil, Telugu,
    # Punjabi, Urdu, Assamese, Sindhi, Nepali, English, and more) and
    # auto-detects language from the input text, so no per-language config
    # is needed here. Leave GEMINI_API_KEY/ELEVENLABS_API_KEY unset to
    # disable; the app remains fully functional either way.
    ELEVENLABS_API_KEY: str | None = None
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"  # ElevenLabs' public "Rachel" voice; override with your own
    ELEVENLABS_MODEL: str = "eleven_multilingual_v2"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
