from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CapstoneAI Back"
    api_prefix: str = "/api"
    kakao_rest_api_key: str
    kakao_redirect_uri: str
    kakao_client_secret: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
