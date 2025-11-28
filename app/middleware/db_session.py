from typing import Callable, Dict, Any, Union
from aiogram import BaseMiddleware
from aiogram.types import Update
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session

class DatabaseSessionMiddleware(BaseMiddleware):
    """Middleware to provide database session to handlers."""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Any],
        update: Update,
        data: Dict[str, Any]
    ) -> Any:
        # Create database session for this update
        async for session in get_session():
            data["session"] = session
            try:
                return await handler(update, data)
            finally:
                await session.close()
