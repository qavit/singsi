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
    OPENAI_API_KEY: SecretStr
    OPENAI_ORG_ID: str | None = None
    DEFAULT_AI_PROVIDER: str = 'openai'
    DEFAULT_AI_MODEL: str = 'gpt-4'

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
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

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
