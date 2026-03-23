import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    log_level: str = "INFO"
    max_retries: int = 3
    timeout: int = 30
    
    class Config:
        env_file = ".env"


settings = Settings()
