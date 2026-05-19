from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "CapstoneAI Back"
    api_prefix: str 
    jwt_secret_key: str = "change-me-in-production"
    jwt_issuer: str = "capstoneai"
    access_token_expire_seconds: int = 60 * 60
    refresh_token_expire_seconds: int = 60 * 60 * 24 * 14
    kakao_rest_api_key: str
    kakao_redirect_uri: str
    kakao_client_secret: str | None = None
    kakao_frontend_redirect_uri: str
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
