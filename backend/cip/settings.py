from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: Literal["local", "production"] = "local"
    frontend_origin: str = "http://localhost:3000"
    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    database_url: str = "postgresql+psycopg://cip:cip@localhost:5432/cip"
    redis_url: str = "redis://localhost:6379/0"

    # "local": plain filesystem, served via /media — zero setup, used by default.
    # "s3": any S3-compatible provider (R2, Supabase Storage, MinIO, ...) — used once deployed.
    storage_backend: Literal["local", "s3"] = "local"
    local_storage_dir: str = "./local_storage"
    backend_public_url: str = "http://localhost:8000"

    storage_endpoint_url: str = ""
    storage_access_key: str = ""
    storage_secret_key: str = ""
    storage_bucket: str = "cip-media"
    storage_region: str = "auto"

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""

    # "stub": deterministic fixtures, no model loaded — fast, used in tests/CI.
    # "local": real in-process YOLO nano detection (CPU) — used in dev and once deployed.
    ai_provider_mode: Literal["stub", "local"] = "stub"

    # Separate axis from ai_provider_mode: detection and report-writing are
    # independent choices (e.g. real local YOLO + stub reports while Groq is
    # being verified). "stub" returns canned text; "groq" calls the real API.
    report_provider_mode: Literal["stub", "groq"] = "stub"
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"

    telegram_bot_token: str = ""
    email_from: str = ""
    resend_api_key: str = ""

    frame_sample_interval_seconds: float = 1.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
