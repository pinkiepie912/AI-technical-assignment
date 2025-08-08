from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["Config"]


class OpenAIConfig(BaseSettings):
    API_KEY: str = Field(default="")

    model_config = SettingsConfigDict(env_prefix="OPENAI_")


class DatabaseConfig(BaseSettings):
    WRITE_ENGINE: str = Field(default="postgresql+asyncpg")
    WRITE_URL: str = Field(default="localhost:5432")
    WRITE_PORT: int = Field(default=5432)
    WRITE_USER: str = Field(default="dev")
    WRITE_PASSWORD: str = Field(default="dev")
    WRITE_DB_NAME: str = Field(default="dev")

    READ_ENGINE: str = Field(default="postgresql+asyncpg")
    READ_URL: str = Field(default="localhost:5432")
    READ_PORT: int = Field(default=5432)
    READ_NAME: str = Field(default="dev")
    READ_USER: str = Field(default="dev")
    READ_PASSWORD: str = Field(default="dev")

    POOL_SIZE: int = Field(default=5)
    MAX_OVERFLOW: int = Field(default=5)
    POOL_TIMEOUT: int = Field(default=30)
    POOL_RECYCLE: int = Field(default=1800)

    model_config = SettingsConfigDict(env_prefix="DB_")


class Config(BaseSettings):
    APP_ENV: str = Field(default="dev")

    OPENAI: OpenAIConfig = Field(default_factory=OpenAIConfig)
    DATABASE: DatabaseConfig = Field(default_factory=DatabaseConfig)

    model_config = SettingsConfigDict(case_sensitive=True)
