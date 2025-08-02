from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str
    sqlite_path: str
    jwt_secret_key: str

    # Cookie settings for dev
    COOKIE_SECURE: bool = Field(False, env="COOKIE_SECURE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra env vars not defined as fields
    )

settings = Settings()
