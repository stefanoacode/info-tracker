from pathlib import Path

from pydantic_settings import BaseSettings

_PROJECT_ROOT = Path(__file__).parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"
DATA_DIR = _PROJECT_ROOT / "data"


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    nitter_instance: str = ""

    model_config = {"env_file": str(_ENV_FILE), "env_file_encoding": "utf-8"}


settings = Settings()
