import pytest
from sqlalchemy import select
from app.models import Order
from app.services.orders import create_order

@pytest.mark.asyncio
async def test_create_order(session):
    # Создание заказа
    order_id = await create_order(
        session=session,
        telegram_id=123456,
        item_id="painting_1",
        payment_method="card",
        delivery_method="pickup"
    )

    # Проверка
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one()

    assert order is not None
    assert order.item_id == "painting_1"
    assert order.status == "pending"
