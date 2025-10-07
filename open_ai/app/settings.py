from pathlib import Path
from functools import lru_cache
from typing import Optional

import os
import tomllib  # Python 3.11+; for 3.10 use: import tomli as tomllib
from pydantic import BaseModel, Field, field_validator

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"

def load_toml_layer(env: Optional[str]) -> dict:
    """
    Load base config + optional environment-specific overlay.
    Later layers (env-specific) override earlier keys shallowly.
    """
    config: dict = {}
    base_file = CONFIG_DIR / "config.toml"
    if base_file.exists():
        with base_file.open("rb") as f:
            config.update(tomllib.load(f))

    if env:
        env_file = CONFIG_DIR / f"config.{env}.toml"
        if env_file.exists():
            with env_file.open("rb") as f:
                env_cfg = tomllib.load(f)
            # Shallow merge
            for k, v in env_cfg.items():
                if isinstance(v, dict) and isinstance(config.get(k), dict):
                    config[k].update(v)
                else:
                    config[k] = v
    return config


class AppSettings(BaseModel):
    # App
    app_name: str = Field(default="app", alias="app_name")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000, env="APP_PORT")
    log_level: str = Field(default="INFO")

    # Database
    db_host: str = Field(default="localhost")
    db_name: str = Field(default="postgres")
    db_port: int = Field(default=5432)
    db_user: str = Field(default="postgres", env="DATABASE_USER")

    # Features
    enable_cache: bool = Field(default=False)

    #azure_open_ai
    azure_openai_endpoint: str = Field(default="")
    azure_openai_key: str = Field(default="")
    azure_openai_version: str = Field(default="")
    azure_openai_embedded_model: str = Field(default="")  # e.g., "text-embedding-3-small"

    #azure_ai_search
    azure_ai_search_endpoint: str = Field(default="")
    azure_ai_search_index_name: str = Field(default="")
    azure_ai_search_key: str = Field(default="")

    # Derived / computed values
    @property
    def database_url(self) -> str:
        return (
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @field_validator("log_level")
    def validate_log_level(cls, v):
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v.upper()

    class Config:
        env_file = BASE_DIR / ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> AppSettings:
    # Determine environment (e.g., DEV, STAGING, PROD)
    env = os.getenv("APP_ENV", "dev").lower()
    raw = load_toml_layer(env if env != "default" else None)

    # Flatten nested sections to align with pydantic fields
    flat = {}
    if "app" in raw:
        flat.update({
            "app_name": raw["app"].get("name"),
            "host": raw["app"].get("host"),
            "port": raw["app"].get("port"),
            "log_level": raw["app"].get("log_level"),
        })
    if "database" in raw:
        flat.update({
            "db_host": raw["database"].get("host"),
            "db_port": raw["database"].get("port"),
            "db_name": raw["database"].get("name"),
        })
    if "features" in raw:
        flat.update({
            "enable_cache": raw["features"].get("enable_cache"),
        })
    if "azure_openai" in raw:
        flat.update({
            "azure_openai_endpoint": raw["azure_openai"].get("endpoint"),
            "azure_openai_key": raw["azure_openai"].get("key"),
            "azure_openai_version": raw["azure_openai"].get("version"),
            "azure_openai_embedded_model": raw["azure_openai"].get("embedded_model"),
        })
    if "azure_ai_search" in raw:
        flat.update({
            "azure_ai_search_endpoint": raw["azure_ai_search"].get("endpoint"),
            "azure_ai_search_index_name": raw["azure_ai_search"].get("index_name"),
            "azure_ai_search_key": raw["azure_ai_search"].get("key"),
        })

    return AppSettings(**{k: v for k, v in flat.items() if v is not None})


if __name__ == "__main__":
    settings = get_settings()
    # Log effective (non-secret) config
    model = settings.model_dump_json()
    print("Effective Settings:", model)
    print("Enable_cache:", settings.enable_cache)
    print("Database URL:", settings.database_url)