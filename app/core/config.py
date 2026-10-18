from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """SCORPGUARD configuration loaded from .env"""
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://scorpguard:scorpguard_pass@localhost:5432/scorpguard"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # vLLM
    VLLM_BASE_URL: str = "http://localhost:8000/v1"
        # Groq Fallback
    GROQ_API_KEY: str = ""
    
    # App
    APP_NAME: str = "SCORPGUARD"
    APP_VERSION: str = "0.1.0"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()