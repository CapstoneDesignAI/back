from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    kakao_rest_api_key: str
    kakao_client_secret: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
