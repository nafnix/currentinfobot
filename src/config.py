from pydantic import DirectoryPath
from pydantic_settings import BaseSettings, SettingsConfigDict
from telegram.constants import ParseMode

from src.constants import Environment, LogLevel


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
        env_prefix="PTB_",
    )

    TOKEN: str

    LOG_LEVEL: LogLevel = LogLevel.DEBUG
    LOG_DIR: DirectoryPath | None = None

    ENVIRONMENT: Environment = Environment.LOCAL

    PARSE_MODE: ParseMode = ParseMode.HTML


settings = Settings()  # pyright: ignore
