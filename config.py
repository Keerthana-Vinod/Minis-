"""
Configuration management for the Food Product Assistant API
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # API Configuration
    api_title: str = "Food Product Assistant API"
    api_version: str = "1.0.0"
    
    # Model Configuration
    model_name: str = "google/gemma-2b-it"
    model_device: str = "cpu"  # "cuda" or "cpu"
    max_new_tokens: int = 512
    temperature: float = 0.7
    
    # CORS Configuration
    allowed_origins: List[str] = ["*"]
    
    # File Upload Configuration
    max_file_size_mb: int = 10
    allowed_image_types: List[str] = ["image/jpeg", "image/png"]
    
    # Logging Configuration
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()
