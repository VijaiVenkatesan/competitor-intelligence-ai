import os
from typing import Optional


class Settings:
    """Application settings"""
    
    def __init__(self):
        self.groq_api_key: str = os.getenv("GROQ_API_KEY", "")
        self.log_level: str = "INFO"
        self.max_retries: int = 3
        self.timeout: int = 30
        self.max_concurrent_requests: int = 3
    
    def validate(self) -> bool:
        """Validate required settings"""
        if not self.groq_api_key:
            return False
        return True


# Global settings instance
settings = Settings()
