"""
Configuration management for OpenHealth Shared Backend
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/openhealth"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "openhealth"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "password"
    
    # AI Services
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Authentication
    JWT_SECRET_KEY: str = "your_super_secret_jwt_key_here_change_this_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # File Storage
    STORAGE_TYPE: str = "local"  # 'local' or 's3'
    LOCAL_STORAGE_PATH: str = "./uploads"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_BUCKET_NAME: Optional[str] = None
    AWS_REGION: str = "us-west-2"
    
    # Email
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@openhealth.com"
    
    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    API_VERSION: str = "v1"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    ALLOW_CREDENTIALS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # AI Models
    DEFAULT_AI_MODEL: str = "claude-3-sonnet-20240229"
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    MAX_TOKENS: int = 4000
    TEMPERATURE: float = 0.7
    
    # Meeting Integration
    CALENDAR_API_KEY: Optional[str] = None
    ZOOM_API_KEY: Optional[str] = None
    ZOOM_API_SECRET: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    ANALYTICS_ENABLED: bool = True
    
    # Security
    ALLOWED_FILE_TYPES: str = "pdf,doc,docx,txt,png,jpg,jpeg"
    MAX_FILE_SIZE_MB: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @property
    def allowed_file_extensions(self) -> List[str]:
        """Get list of allowed file extensions"""
        return [ext.strip().lower() for ext in self.ALLOWED_FILE_TYPES.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes"""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    @property
    def uploads_directory(self) -> Path:
        """Get uploads directory path"""
        path = Path(self.LOCAL_STORAGE_PATH)
        path.mkdir(parents=True, exist_ok=True)
        return path


# Create global settings instance
settings = Settings()
