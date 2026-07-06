import logging
import secrets
from pathlib import Path

from pydantic_settings import BaseSettings
from functools import lru_cache

logger = logging.getLogger(__name__)

_BACKEND_DIR = Path(__file__).resolve().parent.parent
_ENV_FILE = _BACKEND_DIR / ".env"
_DB_PATH = _BACKEND_DIR / "data" / "movies.db"


def _generate_secret_key() -> str:
    return secrets.token_hex(32)


class Settings(BaseSettings):
    app_name: str = "Movie Recommender API"
    gemini_api_key: str = ""
    secret_key: str = ""
    database_url: str = f"sqlite:///{_DB_PATH}"
    access_token_expire_minutes: int = 60  # 1 hour
    algorithm: str = "HS256"

    tmdb_api_key: str = ""
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    debug: bool = False

    model_config = {"env_file": str(_ENV_FILE), "extra": "ignore"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.secret_key:
            self.secret_key = _generate_secret_key()
            logger.warning(
                "SECRET_KEY not set in environment — using a randomly generated key. "
                "Sessions will be invalidated on restart. Set SECRET_KEY in .env for production."
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()
