from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    app_name: str
    sqlite_path: str
    jwt_secret_key: str
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7
    jwt_algorithm: str = "HS256"
    
    # Cookie settings
    cookie_secure: bool
    cookie_httponly: bool
    cookie_samesite: str
    cookie_domain: Optional[str] = None
    
    # Environment settings
    environment: str
    debug: bool
    
    # CORS settings
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra env vars not defined as fields
    )

settings = Settings()
