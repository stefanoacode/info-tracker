from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./data/info_tracker.db"
    anthropic_api_key: str = ""
    youtube_api_key: str = ""
    x_api_bearer_token: str = ""
    collection_interval_hours: int = 6
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
