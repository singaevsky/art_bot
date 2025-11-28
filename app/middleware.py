import time
import logging
from typing import Callable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import Update

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging all updates."""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Any],
        update: Update,
        data: Dict[str, Any]
    ) -> Any:
        start_time = time.time()

        # Log update info
        if update.message:
            logger.info(
                "Message from %s: %s",
                update.message.from_user.id if update.message.from_user else "Unknown",
                update.message.text or update.message.caption or "[media]"
            )
        elif update.callback_query:
            logger.info(
                "Callback from %s: %s",
                update.callback_query.from_user.id if update.callback_query.from_user else "Unknown",
                update.callback_query.data
            )

        try:
            result = await handler(update, data)
            process_time = time.time() - start_time
            logger.info("Update processed in %.2f seconds", process_time)
            return result
        except Exception as e:
            logger.error("Error processing update: %s", e, exc_info=True)
            raise
