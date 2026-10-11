from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    downstream_api_url: str = ""
    downstream_api_key: str = ""
    review_confidence_threshold: float = 0.80
    http_timeout_seconds: float = 10.0
    downstream_max_retries: int = 2

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
