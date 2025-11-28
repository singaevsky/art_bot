from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from ..config import settings
from ..database import get_session, Order
from ..services.orders import update_order_status
from ..states import Admin

router = Router()

@router.message(Command("admin"))
async def admin_cmd(message: Message):
    if message.from_user.id in settings.ADMIN_IDS:
        await message.answer("Добро пожаловать в админ-панель!")
        await Admin.waiting_for_order_id.set()
    else:
        await message.answer("❌ У вас нет доступа к админ-панели.")

@router.message(Admin.waiting_for_order_id)
async def process_order_id(message: Message, state: FSMContext):
    order_id = message.text.strip()
    if not order_id.isdigit():
        await message.answer("Введите корректный ID заказа (только цифры).")
        return

    await state.update_data(order_id=int(order_id))
    await Admin.waiting_for_new_status.set()
    await message.answer("Введите новый статус заказа (pending, confirmed, shipped, delivered, cancelled):")

@router.message(Admin.waiting_for_new_status)
async def process_status(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = data['order_id']
    new_status = message.text.strip().lower()

    valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
    if new_status not in valid_statuses:
        await message.answer(f"Неверный статус. Доступные: {', '.join(valid_statuses)}")
        return

    async for session in get_session():
        await update_order_status(session, order_id, new_status)

    await state.clear()
    await message.answer(f"✅ Статус заказа {order_id} обновлен на {new_status}")
