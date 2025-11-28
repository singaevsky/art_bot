import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.database import init_db, close_db
from app.config import settings, logger
from app.handlers import base_router, shop_router, order_router, admin_router
from app.middleware import (
    LoggingMiddleware,
    DatabaseSessionMiddleware,
    RateLimitingMiddleware,
    ThrottlingMiddleware
)

async def main():
    """Main application entry point."""
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")

        # Create bot instance
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

        # Create storage for FSM
        storage = MemoryStorage()

        # Create dispatcher
        dp = Dispatcher(storage=storage)

        # === ADD ALL MIDDLEWARE (ORDER MATTERS!) ===

        # 1. Logging - logs every update
        dp.update.middleware(LoggingMiddleware())

        # 2. Rate Limiting - prevents spam (max 10 messages per 60 seconds)
        dp.update.middleware(RateLimitingMiddleware(max_messages=10, time_window=60))

        # 3. Throttling - prevents command spam (2 seconds cooldown)
        dp.update.middleware(ThrottlingMiddleware(cooldown=2.0))

        # 4. Database Session - provides DB session to handlers
        dp.update.middleware(DatabaseSessionMiddleware())

        # === REGISTER ALL ROUTERS ===

        # Core handlers
        dp.include_router(base_router)
        dp.include_router(shop_router)
        dp.include_router(order_router)

        # Admin panel (if enabled in config)
        if settings.ENABLE_ADMIN_PANEL:
            dp.include_router(admin_router)

        # Start bot
        logger.info("Bot starting with %d routers", len(dp.router.sub_routers))
        logger.info("Middleware stack: %s",
                   ["Logging", "RateLimit", "Throttle", "Database"])
        await dp.start_polling(bot, drop_pending_updates=True)

    except KeyboardInterrupt:
        logger.info("Received stop signal")
    except Exception as e:
        logger.error("Application error: %s", e, exc_info=True)
    finally:
        await close_db()
        logger.info("Bot stopped and database connections closed")

if __name__ == '__main__':
    try:
        logger.info("Starting Art Bot...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
