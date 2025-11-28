import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Bot Configuration
    TELEGRAM_BOT_TOKEN: str = Field(..., env="TELEGRAM_BOT_TOKEN")

    # Supabase Configuration
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_ANON_KEY: str = Field(..., env="SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY: str = Field(..., env="SUPABASE_SERVICE_KEY")

    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./art_bot.db",
        env="DATABASE_URL"
    )

    # Application Configuration
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Gallery Configuration
    ITEMS_PER_PAGE: int = Field(default=2, env="ITEMS_PER_PAGE", ge=1, le=10)
    ORDER_DEDUP_MINUTES: int = Field(default=10, env="ORDER_DEDUP_MINUTES", ge=1, le=60)

    # Validation
    MAX_ADDRESS_LENGTH: int = Field(default=200, env="MAX_ADDRESS_LENGTH")
    MAX_NAME_LENGTH: int = Field(default=100, env="MAX_NAME_LENGTH")

    # Feature Flags
    ENABLE_ADMIN_PANEL: bool = Field(default=True, env="ENABLE_ADMIN_PANEL")
    ENABLE_GIFT_SYSTEM: bool = Field(default=True, env="ENABLE_GIFT_SYSTEM")
    ENABLE_FAQ: bool = Field(default=True, env="ENABLE_FAQ")

    @field_validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'LOG_LEVEL must be one of {valid_levels}')
        return v.upper()


    class Config:
        env_file = BASE_DIR / '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = 'ignore'

import logging

settings = Settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.LOG_LEVEL))

# Load ADMIN_IDS from environment manually to handle comma-separated values
ADMIN_IDS: list[int] = []
admin_ids_str = os.getenv("ADMIN_IDS", "")
if admin_ids_str:
    ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(',') if x.strip()]

# Database configuration helper
def get_database_url() -> str:
    """Get database URL based on environment."""
    if "postgresql" in settings.DATABASE_URL.lower():
        return settings.DATABASE_URL
    else:
        # Fallback to SQLite for development
        return "sqlite+aiosqlite:///./art_bot.db"

def get_database_url_safe() -> str:
    """Safely get database URL with fallback for migrations."""
    try:
        if "postgresql" in settings.DATABASE_URL.lower():
            return settings.DATABASE_URL
        else:
            # Fallback to SQLite for development
            return "sqlite+aiosqlite:///./art_bot.db"
    except Exception:
        # If there's any error accessing the settings, fallback to SQLite
        return "sqlite+aiosqlite:///./art_bot.db"
