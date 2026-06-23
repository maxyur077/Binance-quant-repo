from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

env_state = os.getenv("APP_ENV", "dev")
env_file = f".env.{env_state}" if env_state != "dev" else ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, env_file_encoding="utf-8", extra="ignore")
    
    APP_ENV: str = env_state
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ENCRYPTION_KEY: str = ""

    PHANTOM_RECEIVING_WALLET: str = ""
    SOLANA_RPC_URL: str = "https://api.mainnet-beta.solana.com"

    CORS_ORIGINS: str = "http://localhost:3000"

    MAX_USER_LIMIT: int = 100
    SUBSCRIPTION_PRICE_USD: float = 50.0
    TRIAL_DURATION_DAYS: int = 7
    DEBUG: bool = False

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
