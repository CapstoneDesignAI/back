from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "CapstoneAI Back"
    api_prefix: str = "/api/v1"
    jwt_secret_key: str = "change-me-in-production"
    jwt_issuer: str = "capstoneai"
    access_token_expire_seconds: int = 60 * 60
    refresh_token_expire_seconds: int = 60 * 60 * 24 * 14
    kakao_rest_api_key: str = ""
    kakao_redirect_uri: str = "http://127.0.0.1:8000/api/v1/auth/kakao/callback"
    kakao_client_secret: str | None = None
    kakao_frontend_redirect_uri: str = "http://localhost:8081/auth/callback"
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    mission_upload_bucket: str = "mission-verifications"
    tour_api_service_key: str | None = None
    tour_api_base_url: str = "https://apis.data.go.kr/B551011/KorService2"
    tour_api_service_version: str = "2"
    tour_api_mobile_os: str = "ETC"
    tour_api_mobile_app: str = "TRIP_RE"
    odsay_api_key: str | None = None
    odsay_api_base_url: str = "https://api.odsay.com/v1/api"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
