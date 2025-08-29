from pydantic_settings import BaseSettings
from typing import Optional
import os


class TallySettings(BaseSettings):
    """Configuration settings for TallyDash application."""
    
    # Tally ODBC Configuration
    tally_host: str = "localhost"
    tally_port: int = 9000
    odbc_driver: str = "Tally ODBC Driver"
    connection_timeout: int = 30
    max_connections: int = 5
    retry_attempts: int = 3
    
    # AI Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    copilot_api_key: Optional[str] = None
    
    # Application Configuration
    app_title: str = "TallyDash"
    app_description: str = "AI-Powered Tally ERP Dashboard"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 3000
    
    # Security Configuration
    secret_key: str = "your-secret-key-change-this-in-production"
    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database Configuration
    cache_ttl: int = 300  # 5 minutes
    max_query_results: int = 10000
    query_timeout: int = 60
    
    # Redis Configuration (for caching)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def tally_connection_string(self) -> str:
        """Generate ODBC connection string for Tally."""
        return (
            f"DRIVER={{{self.odbc_driver}}};"
            f"SERVER={self.tally_host};"
            f"PORT={self.tally_port};"
        )
    
    @property
    def redis_url(self) -> str:
        """Generate Redis connection URL."""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"


# Global settings instance
settings = TallySettings()