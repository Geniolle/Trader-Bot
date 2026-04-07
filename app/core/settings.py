from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Market Research Lab")
    app_env: str = Field(default="development")
    app_debug: bool = Field(default=True)
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)

    log_level: str = Field(default="INFO")
    timezone: str = Field(default="UTC")

    market_data_provider: str = Field(default="mock")

    twelvedata_api_key: str = Field(default="")
    twelvedata_base_url: str = Field(default="https://api.twelvedata.com")

    database_url: str = Field(default="sqlite:///./market_research_lab.db")

    candles_bootstrap_limit_intraday: int = Field(default=240)
    candles_bootstrap_limit_daily: int = Field(default=120)
    candles_gap_fill_max_bars: int = Field(default=500)
    provider_quota_cooldown_minutes: int = Field(default=30)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()