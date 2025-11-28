"""
Telegram Bot for Art Gallery
A modern aiogram 3.x bot with async SQLAlchemy database support.
"""

from .config import settings
from .database import init_db, get_session

__version__ = "1.0.0"
__all__ = ["settings", "init_db", "get_session"]
