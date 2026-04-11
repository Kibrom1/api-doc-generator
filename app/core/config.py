from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    anthropic_api_key: str
    claude_model: str = "claude-sonnet-4-6"

    # Repo analyzer limits
    max_repo_file_size_kb: int = 100
    max_repo_files: int = 30

    # Endpoint analyzer
    request_timeout_seconds: int = 30

    # Storage
    output_dir: str = "output"


settings = Settings()
