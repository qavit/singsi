import secrets
from typing import Any, ClassVar

from pydantic import AnyHttpUrl, Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS allowed origins
    BACKEND_CORS_ORIGINS: ClassVar[list[AnyHttpUrl]] = []

    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith('['):
            return [i.strip() for i in v.split(',')]
        elif isinstance(v, list | str):
            return v
        raise ValueError(v)

    # Database settings
    POSTGRES_SERVER: str = 'localhost'
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres'
    POSTGRES_DB: str = 'app'
    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None

    @classmethod
    def build_db_uri(cls, values: dict[str, Any]) -> str | None:
        if isinstance(values.get('SQLALCHEMY_DATABASE_URI'), str):
            return values['SQLALCHEMY_DATABASE_URI']
        return str(
            PostgresDsn.build(
                scheme='postgresql',
                username=values.get('POSTGRES_USER'),
                password=values.get('POSTGRES_PASSWORD'),
                host=values.get('POSTGRES_SERVER', ''),
                path=f'/{values.get("POSTGRES_DB", "")}',
            )
        )

    # AI model configuration
    AI_MODEL_PATH: str = 'models/ai_model'

    # Redis configuration (for async tasks)
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379

    model_config = SettingsConfigDict(case_sensitive=True, env_file='.env')


settings = Settings()
