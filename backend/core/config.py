from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    SYNC_DATABASE_URL: str = "sqlite:///./fitapp.db"
    ASYNC_DATABASE_URL: str = "sqlite+aiosqlite:///./fitapp.db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False
    DB_CONNECT_ARGS: dict = {"check_same_thread": False}
    SQLITE_DB_PATH: str = "sqlite:///C:/Users/misti/Desktop/App/fitapp.db"
    ASYNC_SQLITE_DB_PATH: str = "sqlite+aiosqlite:///C:/Users/misti/Desktop/App/fitapp.db"
    SECRET_KEY: str = "tuo-segreto-super-securo"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Auth
    DEV_MODE: bool = True
    POPULATE_TEST_DATA: bool = False
    CORS_ALLOWED_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
