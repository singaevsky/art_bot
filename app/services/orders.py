from sqlalchemy import select, insert, update, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from ..models import Order, OrderEvent, GalleryItem
from ..config import settings

class OrderService:
    """Service for order management."""

    @staticmethod
    async def create_order(
        session: AsyncSession,
        telegram_id: int,
        item_id: str,
        payment_method: str,
        delivery_method: str,
        address: str = None
    ) -> int:
        """Create new order with deduplication."""

        # Check for recent duplicate orders
        dedup_cutoff = datetime.utcnow() - timedelta(minutes=settings.ORDER_DEDUP_MINUTES)
        recent_order = await session.execute(
            select(Order).where(
                and_(
                    Order.telegram_id == telegram_id,
                    Order.item_id == item_id,
                    Order.status.in_(['pending', 'confirmed']),
                    Order.order_date >= dedup_cutoff
                )
            )
        )

        if recent_order.scalar_one_or_none():
            raise ValueError("Duplicate order attempt detected")

        # Create order
        result = await session.execute(
            insert(Order).values(
                telegram_id=telegram_id,
                item_id=item_id,
                payment_method=payment_method,
                delivery_method=delivery_method,
                delivery_address=address,
                status='pending',
                order_date=datetime.utcnow()
            )
        )
        order_id = result.inserted_primary_key[0]

        # Add initial event
        await session.execute(
            insert(OrderEvent).values(
                order_id=order_id,
                status='pending',
                comment='Order created'
            )
        )

        await session.commit()
        return order_id

    @staticmethod
    async def get_user_orders(session: AsyncSession, telegram_id: int, limit: int = 10):
        """Get user's orders with item details."""
        result = await session.execute(
            select(Order, GalleryItem)
            .join(GalleryItem, Order.item_id == GalleryItem.id)
            .where(Order.telegram_id == telegram_id)
            .order_by(desc(Order.order_date))
            .limit(limit)
        )
        return result.all()

    @staticmethod
    async def get_order(session: AsyncSession, order_id: int) -> Order:
        """Get order by ID."""
        result = await session.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_order_status(
        session: AsyncSession,
        order_id: int,
        new_status: str,
        comment: str = None
    ) -> bool:
        """Update order status and create event."""
        result = await session.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(
                status=new_status,
                updated_at=datetime.utcnow()
            )
            .returning(Order.id)
        )

        if result.scalar_one_or_none():
            await session.execute(
                insert(OrderEvent).values(
                    order_id=order_id,
                    status=new_status,
                    comment=comment
                )
            )
            await session.commit()
            return True

        return False

    @staticmethod
    async def get_pending_orders(session: AsyncSession, limit: int = 50):
        """Get pending orders for admin view."""
        result = await session.execute(
            select(Order, GalleryItem)
            .join(GalleryItem, Order.item_id == GalleryItem.id)
            .where(Order.status == 'pending')
            .order_by(desc(Order.order_date))
            .limit(limit)
        )
        return result.all()

    @staticmethod
    async def get_order_events(session: AsyncSession, order_id: int):
        """Get order events/history."""
        result = await session.execute(
            select(OrderEvent)
            .where(OrderEvent.order_id == order_id)
            .order_by(OrderEvent.created_at)
        )
        return result.scalars().all()
