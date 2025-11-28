import time
from typing import Dict, Set, Callable, Any
from aiogram import BaseMiddleware
from aiogram.types import Update
import logging

logger = logging.getLogger(__name__)

class RateLimitingMiddleware(BaseMiddleware):
    """Simple rate limiting middleware."""

    def __init__(self, max_messages: int = 5, time_window: int = 60):
        self.max_messages = max_messages
        self.time_window = time_window
        self.user_messages: Dict[int, list] = {}

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Any],
        update: Update,
        data: Dict[str, Any]
    ) -> Any:
        # Skip rate limiting for updates without a user or message
        if not update.message or not update.message.from_user:
            return await handler(update, data)

        user_id = update.message.from_user.id
        current_time = time.time()

        # Clean old messages
        if user_id in self.user_messages:
            self.user_messages[user_id] = [
                msg_time for msg_time in self.user_messages[user_id]
                if current_time - msg_time < self.time_window
            ]

        # Check rate limit
        if user_id in self.user_messages:
            if len(self.user_messages[user_id]) >= self.max_messages:
                await update.message.answer(
                    "⏳ Слишком много сообщений. Подождите немного."
                )
                return  # Skip handler

        # Record this message
        if user_id not in self.user_messages:
            self.user_messages[user_id] = []
        self.user_messages[user_id].append(current_time)

        return await handler(update, data)
