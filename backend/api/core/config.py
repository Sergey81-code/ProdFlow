from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "ProdFlow"
    VERSION: str = "1.0.0"

    ASYNC_REAL_DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5435/prodflow"
    )
    TEST_DATABASE_URL: str = (
        "postgresql+asyncpg://postgres_test:postgres_test@localhost:5429/postgres_test"
    )
    SECRET_KEY_FOR_ACCESS: str = "your-strong-access-secret-key"
    ALGORITHM: str = "HS256"
    APP_PORT: int = 8000
    ENABLE_PERMISSION_CHECK: bool = True
    TOKEN_EXPIRE_MINUTES: int = 60 * 23

    class Config:
        env_file = "config/.env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    return Settings()
