"""
Configuration settings for the AI Firewall service
"""
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """
    Application configuration settings
    
    Settings can be overridden via environment variables
    """
    
    # Application
    app_name: str = "AI Firewall Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # AI Service
    ai_score_threshold_block: float = 0.8
    ai_score_threshold_alert: float = 0.5
    
    # CORS (for development/testing)
    cors_enabled: bool = True
    cors_origins: list[str] = ["*"]
    
    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "firewall_ai"
    db_user: str = "firewall_user"
    db_password: str = "firewall_password"
    db_pool_min_size: int = 2
    db_pool_max_size: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
