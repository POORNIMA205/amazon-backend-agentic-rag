"""
Centralized application configuration.
All environment-driven settings live here so nothing is hardcoded
across the codebase.
"""
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "Amazon-Backend"
    ENV: str = "development"

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./amazon.db"

    # --- Auth / JWT ---
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_9f8a7d6c5b4e3f2a1"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # --- Logging ---
    LOG_DIR: str = "logs"
    LOG_FILE: str = "app.log"
    LOG_LEVEL: str = "INFO"

    # --- Ollama ---
    ollama_enabled: bool = True
    ollama_model: str = "llama3.2"
    ollama_timeout_seconds: int = 8

    class Config:
        env_file = ".env"


settings = Settings()
