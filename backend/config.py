from pathlib import Path

from pydantic_settings import BaseSettings

# Resolve .env relative to the project root (where pyproject.toml lives)
_PROJECT_ROOT = Path(__file__).parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"
_DATA_DIR = _PROJECT_ROOT / "data"


class Settings(BaseSettings):
    database_url: str = f"sqlite:///{_DATA_DIR}/info_tracker.db"
    anthropic_api_key: str = ""
    youtube_api_key: str = ""
    nitter_instance: str = ""  # Leave blank to try public instances
    digest_frequency_hours: int = 6

    model_config = {"env_file": str(_ENV_FILE), "env_file_encoding": "utf-8"}


settings = Settings()
