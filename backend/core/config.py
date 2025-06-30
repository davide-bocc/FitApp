from pydantic_settings import BaseSettings
from typing import List, Optional
from pathlib import Path
import os


class Settings(BaseSettings):
    # Database
    SYNC_DATABASE_URL: str = "sqlite:///./fitapp.db"
    ASYNC_DATABASE_URL: str = "sqlite+aiosqlite:///./fitapp.db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False
    DB_CONNECT_ARGS: dict = {"check_same_thread": False}

    # Path assoluti (solo per sviluppo)
    if os.name == 'nt':  # Windows
        SQLITE_DB_PATH: str = str(Path('C:/Users/misti/Desktop/App/fitapp.db').absolute())
    else:  # Linux/Mac
        SQLITE_DB_PATH: str = str(Path.home() / 'Desktop/App/fitapp.db')

    ASYNC_SQLITE_DB_PATH: str = f"sqlite+aiosqlite:///{SQLITE_DB_PATH}"

    # JWT Configuration
    SECRET_KEY: str = "tuo-segreto-super-securo"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Nuova configurazione

    # Auth & Security
    DEV_MODE: bool = True
    POPULATE_TEST_DATA: bool = False
    CORS_ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    SECURE_COOKIES: bool = not DEV_MODE
    SESSION_TIMEOUT: int = 3600  # 1 ora

    # Logging Configuration (Nuova sezione)
    LOG_LEVEL: str = "DEBUG" if DEV_MODE else "INFO"
    LOG_FILE: str = str(Path('logs/app.log').absolute())
    LOG_ROTATION: str = "10 MB"  # Rotazione log
    LOG_RETENTION: str = "7 days"  # Conservazione log
    LOG_SENSITIVE_FILTER: bool = True  # Filtra dati sensibili

    # Email (configurazione di esempio)
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "ignore"

        @classmethod
        def customise_sources(
                cls,
                init_settings,
                env_settings,
                file_secret_settings,
        ):
            # Disabilita i secrets se non in produzione
            if not cls().DEV_MODE:
                return init_settings, env_settings
            return init_settings, env_settings, file_secret_settings

    @property
    def database_config(self):
        """Configurazione database strutturata"""
        return {
            "sync_url": self.SYNC_DATABASE_URL,
            "async_url": self.ASYNC_DATABASE_URL,
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "echo": self.DB_ECHO,
            "connect_args": self.DB_CONNECT_ARGS
        }

    @property
    def jwt_config(self):
        """Configurazione JWT strutturata"""
        return {
            "secret_key": self.SECRET_KEY,
            "algorithm": self.ALGORITHM,
            "access_expire": self.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "refresh_expire": self.REFRESH_TOKEN_EXPIRE_DAYS * 86400
        }


settings = Settings()

# Validazione aggiuntiva
if settings.DEV_MODE and "*" in settings.CORS_ALLOWED_ORIGINS:
    print("⚠️ Attenzione: CORS con wildcard (*) in DEV_MODE")