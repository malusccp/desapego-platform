from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações carregadas de variáveis de ambiente / arquivo .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "Desapego API"
    API_V1_PREFIX: str = "/api/v1"

    # Trocar para postgresql+psycopg://user:pass@host/db na migração
    DATABASE_URL: str = "sqlite:///./desapego.db"

    # JWT
    SECRET_KEY: str = "troque-esta-chave-em-producao"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Origens liberadas para o frontend (Vite roda em 5173 por padrão)
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
