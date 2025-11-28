"""
Telegram bot handlers.
"""

from .base import router as base_router
from .shop import router as shop_router
from .orders import router as order_router
from .admin import router as admin_router

__all__ = ["base_router", "shop_router", "order_router", "admin_router"]
