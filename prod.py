"""
Production server runner with optimizations.
"""

import asyncio
import logging
from aiogram.fsm.storage.redis import RedisStorage
from main import main
from app.config import settings

async def main_prod():
    """Production optimized main function."""
    try:
        # Use Redis storage for production
        storage = RedisStorage.from_url(settings.REDIS_URL)

        # Lower log level for production
        logging.basicConfig(
            level=logging.WARNING,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        logger = logging.getLogger(__name__)
        logger.info("🏭 Starting in PRODUCTION mode")
        logger.info("Redis storage: %s", settings.REDIS_URL)
        logger.info("Admin panel enabled: %s", settings.ENABLE_ADMIN_PANEL)

        # Call main function with production settings
        await main()

    except Exception as e:
        logging.error("Production error: %s", e)
        raise

if __name__ == "__main__":
    asyncio.run(main_prod())
