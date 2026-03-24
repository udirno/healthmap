from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # API Keys (optional so app can start without them; AI/weather features degrade gracefully)
    ANTHROPIC_API_KEY: str = ""
    OPENWEATHER_API_KEY: str = ""

    # CORS - now a string, we'll split it
    CORS_ORIGINS: str = "http://localhost:3000"

    # App
    APP_NAME: str = "HealthMap API"
    DEBUG: bool = True

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
