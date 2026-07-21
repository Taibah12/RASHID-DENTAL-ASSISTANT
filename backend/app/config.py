from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Port & Environment
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    
    # Security Keys
    GEMINI_API_KEY: str
    
    # Database
    DATABASE_URL: Optional[str] = None

    # Load from actual .env file locally
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

# Instantiate settings globally
settings = Settings()