import os
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Gradually AI"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Default value for development
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React frontend
        "http://localhost:8000",  # Backend (for development)
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",  # Vite dev server (alternative)
        "http://localhost:5174",  # Vite preview
        "http://127.0.0.1:5174",  # Vite preview (alternative)
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = "logs/app.log"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PREFIX: str = "gradually_ai"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_file_encoding='utf-8',
        extra='allow'  # Allow extra fields in the environment
    )

# Create settings instance
settings = Settings()

# Ensure logs directory exists
if settings.LOG_FILE:
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(exist_ok=True) 