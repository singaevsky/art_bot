"""
Development server runner with hot reload and debug info.
"""

import asyncio
import logging
from main import main
from app.config import settings

if __name__ == "__main__":
    # Set development logging level
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting in DEVELOPMENT mode")
    logger.info("Features enabled: %s", {
        "Admin Panel": settings.ENABLE_ADMIN_PANEL,
        "Gift System": settings.ENABLE_GIFT_SYSTEM,
        "FAQ": settings.ENABLE_FAQ,
        "Debug": settings.DEBUG
    })

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Development server stopped")
