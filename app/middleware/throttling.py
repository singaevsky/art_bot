from typing import Dict, Any, Callable
from aiogram import BaseMiddleware
from aiogram.types import Update
import asyncio

class ThrottlingMiddleware(BaseMiddleware):
    """Prevent command spam."""

    def __init__(self, cooldown: float = 1.0):
        self.cooldown = cooldown
        self.last_message: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Any],
        update: Update,
        data: Dict[str, Any]
    ) -> Any:
        user_id = update.message.from_user.id if update.message else 0

        if user_id in self.last_message:
            if asyncio.get_event_loop().time() - self.last_message[user_id] < self.cooldown:
                if update.message:
                    await update.message.answer("⏳ Не торопитесь, подождите...")
                return

        self.last_message[user_id] = asyncio.get_event_loop().time()
        return await handler(update, data)
