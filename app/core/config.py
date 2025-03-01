from pathlib import Path
from typing import ClassVar

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    APP_ENV: str = 'development'
    DEBUG: bool = True
    SECRET_KEY: str = Field(default_factory=lambda: 'dev-secret-key')
    API_V1_STR: str = '/api/v1'

    # AI Settings
    DEFAULT_AI_PROVIDER: str = 'openai'
    OPENAI_API_KEY: SecretStr
    OPENAI_ORG_ID: str | None = None
    OPENAI_DEFAULT_MODEL: str = 'gpt-4o-mini'

    # CORS
    BACKEND_CORS_ORIGINS: ClassVar[list[AnyHttpUrl]] = []

    # Database
    POSTGRES_SERVER: str = 'localhost'
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres'
    POSTGRES_DB: str = 'app'
    POSTGRES_PORT: str = '5432'

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Get async database URI."""
        user = self.POSTGRES_USER
        password = self.POSTGRES_PASSWORD
        server = self.POSTGRES_SERVER
        port = self.POSTGRES_PORT
        db = self.POSTGRES_DB
        return f'postgresql+asyncpg://{user}:{password}@{server}:{port}/{db}'

    # Redis
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    REDIS_DB: int = 0

    # Storage
    STORAGE_PROVIDER: str = 'local'
    STORAGE_ROOT: str = str(Path(__file__).parent.parent.parent / 'storage')
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: SecretStr | None = None
    AWS_REGION: str | None = None
    S3_BUCKET: str | None = None

    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith('['):
            return [i.strip() for i in v.split(',')]
        elif isinstance(v, list | str):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        case_sensitive=True, env_file='.env', extra='ignore'
    )


settings = Settings()
