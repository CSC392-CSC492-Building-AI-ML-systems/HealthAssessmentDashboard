from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "OurPATHS API"
    mongo_uri: str
    mongo_db: str = "ourpaths_dev"
    sqlite_path: str = "sqlite+aiosqlite:///./dev.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()
