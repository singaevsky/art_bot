from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from ..models import User

class UserService:
    """Service for user management."""

    @staticmethod
    async def get_or_create_user(session: AsyncSession, telegram_id: int) -> User:
        """Get existing user or create new one."""
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

        if not user:
            user = User(telegram_id=telegram_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)

        return user

    @staticmethod
    async def update_subscription(session: AsyncSession, telegram_id: int, subscribed: bool) -> bool:
        """Update user subscription status."""
        result = await session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(subscribed=subscribed, updated_at=datetime.utcnow())
            .returning(User.id)
        )
        await session.commit()
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def is_subscribed(session: AsyncSession, telegram_id: int) -> bool:
        """Check if user is subscribed."""
        result = await session.execute(select(User.subscribed).where(User.telegram_id == telegram_id))
        return result.scalar_one() or False

    @staticmethod
    async def has_received_gift(session: AsyncSession, telegram_id: int) -> bool:
        """Check if user has received gift."""
        result = await session.execute(select(User.received_gift).where(User.telegram_id == telegram_id))
        return result.scalar_one() or False

    @staticmethod
    async def generate_promo_code(session: AsyncSession, telegram_id: int) -> str:
        """Generate promo code for user."""
        import secrets
        promo_code = f"HappyDay{secrets.token_hex(4).upper()}"

        await session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(promo_code=promo_code, received_gift=True, updated_at=datetime.utcnow())
        )
        await session.commit()
        return promo_code

    @staticmethod
    async def get_user_promo_code(session: AsyncSession, telegram_id: int) -> str | None:
        """Get user's promo code."""
        result = await session.execute(select(User.promo_code).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def unsubscribe_user(session: AsyncSession, telegram_id: int) -> bool:
        """Unsubscribe user and invalidate promo code."""
        result = await session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(
                subscribed=False,
                received_gift=False,
                promo_code=None,
                updated_at=datetime.utcnow()
            )
            .returning(User.id)
        )
        await session.commit()
        return result.scalar_one_or_none() is not None
