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
        if update.message and update.message.from_user:
            logger.info(
                "Message from %s: %s",
                update.message.from_user.id,
                update.message.text or update.message.caption or "[media]"
            )
        elif update.callback_query and update.callback_query.from_user:
            logger.info(
                "Callback from %s: %s",
                update.callback_query.from_user.id,
                update.callback_query.data
            )
        elif update.inline_query and update.inline_query.from_user:
            logger.info(
                "Inline query from %s: %s",
                update.inline_query.from_user.id,
                update.inline_query.query
            )

        try:
            result = await handler(update, data)
            process_time = time.time() - start_time
            logger.info("Update processed in %.2f seconds", process_time)
            return result
        except Exception as e:
            logger.error("Error processing update: %s", e, exc_info=True)
            raise
