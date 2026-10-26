
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./local.db"
    jwt_secret_key: str = "local-development-secret-change-me"
    access_token_minutes: int = 480
    mock_api_url: str = "http://localhost:8001"
    scoring_api_url: str = ""
    scoring_timeout_seconds: float = 15
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
