import pytest
from app.config import settings

def test_config_loading():
    """Test that configuration loads correctly."""
    assert settings.TELEGRAM_BOT_TOKEN is not None
    assert settings.DATABASE_URL is not None

def test_admin_ids_parsing():
    """Test admin IDs parsing from string."""
    # This would be tested with actual .env values
    assert isinstance(settings.ADMIN_IDS, list)

def test_validation():
    """Test validation settings."""
    assert settings.ITEMS_PER_PAGE >= 1
    assert settings.ITEMS_PER_PAGE <= 10
    assert settings.ORDER_DEDUP_MINUTES >= 1
