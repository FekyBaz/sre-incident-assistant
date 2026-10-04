from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SRE Incident Assistant"
    app_env: str = "development"
    log_level: str = "INFO"
    llm_provider: str = "gemini"
    llm_api_key: str = ""
    llm_model: str = ""
    github_token: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
