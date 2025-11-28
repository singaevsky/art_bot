"""
Order creation and management handlers.
"""

from typing import Dict, Any
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, insert, and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from ..database import get_session, Order, OrderEvent
from ..services.orders import OrderService
from ..services.gallery import GalleryService
from ..keyboards import confirm_order_keyboard
from ..states import OrderCreate
from ..config import settings
from ..utils.validators import validate_address, format_price

router = Router()

PAYMENT_METHODS = {
    "card": "💳 Банковская карта",
    "sbp": "⚡ СБП (Система быстрых платежей)",
    "cash": "💵 Наличные при получении"
}

DELIVERY_METHODS = {
    "pickup": "🏪 Самовывоз",
    "delivery": "🚚 Доставка по адресу"
}

@router.callback_query(F.data.startswith("select_item_"))
async def select_item_handler(query: CallbackQuery, state: FSMContext):
    """Handle item selection for purchase."""
    item_id = query.data.split("_", 2)[2]  # select_item_{item_id}

    # Store item ID and move to payment selection
    await state.set_state(OrderCreate.choose_payment)
    await state.update_data(item_id=item_id)

    # Show payment methods
    await query.message.edit_text(
        "💳 <b>Выберите способ оплаты:</b>\n\n"
        "Доступные способы оплаты:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(PAYMENT_METHODS["card"], callback_data=f"pay_card_{item_id}")],
            [InlineKeyboardButton(PAYMENT_METHODS["sbp"], callback_data=f"pay_sbp_{item_id}")],
            [InlineKeyboardButton(PAYMENT_METHODS["cash"], callback_data=f"pay_cash_{item_id}")],
            [InlineKeyboardButton("⬅️ Назад к товару", callback_data=f"item_{item_id}")],
            [InlineKeyboardButton("🛍 Назад в магазин", callback_data="shop")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ])
    )

@router.callback_query(F.data.startswith("pay_"))
async def payment_handler(query: CallbackQuery, state: FSMContext):
    """Handle payment method selection."""
    # Parse callback data: pay_{method}_{item_id}
    parts = query.data.split("_")
    if len(parts) < 3:
        await query.answer("❌ Неверные данные", show_alert=True)
        return

    payment_method = parts[1]
    item_id = parts[2]

    # Validate payment method
    if payment_method not in PAYMENT_METHODS:
        await query.answer("❌ Неизвестный способ оплаты", show_alert=True)
        return

    # Store payment method and move to delivery selection
    await state.set_state(OrderCreate.choose_delivery)
    await state.update_data(payment_method=payment_method)

    # Show delivery methods
    await query.message.edit_text(
        f"💳 <b>Способ оплаты выбран:</b> {PAYMENT_METHODS[payment_method]}\n\n"
        f"🎨 Товар: {GalleryService.get_item(item_id)['name']}\n\n"
        f"💰 Цена: {format_price(GalleryService.get_item(item_id)['price'])} руб.\n\n"
        "🚚 <b>Выберите способ получения:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(DELIVERY_METHODS["pickup"], callback_data=f"deliver_pickup_{payment_method}_{item_id}")],
            [InlineKeyboardButton(DELIVERY_METHODS["delivery"], callback_data=f"deliver_delivery_{payment_method}_{item_id}")],
            [InlineKeyboardButton("⬅️ Назад к оплате", callback_data=f"pay_{payment_method}_{item_id}")],
            [InlineKeyboardButton("🛍 Назад в магазин", callback_data="shop")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ])
    )

@router.callback_query(F.data.startswith("deliver_"))
async def delivery_handler(query: CallbackQuery, state: FSMContext):
    """Handle delivery method selection."""
    # Parse callback data: deliver_{method}_{payment}_{item_id}
    parts = query.data.split("_")
    if len(parts) < 4:
        await query.answer("❌ Неверные данные", show_alert=True)
        return

    delivery_method = parts[1]
    payment_method = parts[2]
    item_id = parts[3]

    # Validate delivery method
    if delivery_method not in DELIVERY_METHODS:
        await query.answer("❌ Неизвестный способ доставки", show_alert=True)
        return

    item = GalleryService.get_item(item_id)
    if not item:
        await query.answer("❌ Товар не найден", show_alert=True)
        return

    await state.update_data(delivery_method=delivery_method)

    if delivery_method == "delivery":
        # Request delivery address
        await state.set_state(OrderCreate.input_address)
        await query.message.edit_text(
            f"🚚 <b>Доставка по адресу</b>\n\n"
            f"🎨 Товар: {item['name']}\n"
            f"💰 Цена: {format_price(item['price'])} руб.\n"
            f"💳 Оплата: {PAYMENT_METHODS[payment_method]}\n\n"
            f"📍 <b>Введите адрес доставки:</b>\n\n"
            f"Пример: г. Москва, ул. Тверская, д. 1, кв. 1",
            parse_mode="HTML"
        )
    else:
        # Pickup - confirm order directly
        await finalize_order(query, state, address=None)

@router.message(OrderCreate.input_address)
async def address_input(message: Message, state: FSMContext):
    """Handle delivery address input."""
    if not message.text:
        await message.answer("❌ Пожалуйста, введите текстовый адрес.")
        return

    address = message.text.strip()

    # Validate address
    is_valid, sanitized_address = validate_address(address)
    if not is_valid:
        await message.answer(f"❌ {sanitized_address}\n\nПопробуйте еще раз.")
        return

    # Finalize order with address
    await finalize_order(message, state, address=sanitized_address)

@router.callback_query(F.data.startswith("confirm_order_"))
async def confirm_order_handler(query: CallbackQuery, state: FSMContext):
    """Handle order confirmation."""
    # Parse callback data: confirm_order_{item_id}_{payment_method}_{delivery_method}
    parts = query.data.split("_")
    if len(parts) < 5:
        await query.answer("❌ Неверные данные", show_alert=True)
        return

    item_id = parts[2]
    payment_method = parts[3]
    delivery_method = parts[4]

    # Update state with final data
    await state.update_data(
        item_id=item_id,
        payment_method=payment_method,
        delivery_method=delivery_method
    )

    await finalize_order(query, state, address=None)

async def finalize_order(source: CallbackQuery | Message, state: FSMContext, address: str | None):
    """Finalize order creation."""
    data = await state.get_data()

    # Extract data
    user_id = source.from_user.id
    item_id = data.get("item_id")
    payment_method = data.get("payment_method")
    delivery_method = data.get("delivery_method")

    if not all([user_id, item_id, payment_method, delivery_method]):
        error_msg = "❌ Ошибка: не все данные заказа заполнены."
        if isinstance(source, CallbackQuery):
            await source.message.edit_text(error_msg, reply_markup=get_shop_menu())
        else:
            await source.answer(error_msg)
        await state.clear()
        return

    item = GalleryService.get_item(item_id)
    if not item:
        error_msg = "❌ Товар не найден."
        if isinstance(source, CallbackQuery):
            await source.message.edit_text(error_msg, reply_markup=get_shop_menu())
        else:
            await source.answer(error_msg)
        await state.clear()
        return

    try:
        # Create order
        async for session in get_session():
            order_id = await OrderService.create_order(
                session=session,
                telegram_id=user_id,
                item_id=item_id,
                payment_method=payment_method,
                delivery_method=delivery_method,
                address=address
            )

        # Format success message
        success_msg = (
            f"✅ <b>Заказ успешно оформлен!</b>\n\n"
            f"🆔 <b>Номер заказа:</b> #{order_id}\n"
            f"🎨 <b>Товар:</b> {item['name']}\n"
            f"💰 <b>Цена:</b> {format_price(item['price'])} руб.\n"
            f"💳 <b>Оплата:</b> {PAYMENT_METHODS[payment_method]}\n"
            f"🚚 <b>Получение:</b> {DELIVERY_METHODS[delivery_method]}\n"
        )

        if address:
            success_msg += f"📍 <b>Адрес доставки:</b> {address}\n"

        success_msg += (
            f"\n⏳ <b>Статус:</b> В обработке\n"
            f"📞 <b>Мы свяжемся с вами для подтверждения заказа.</b>"
        )

        # Send success message
        if isinstance(source, CallbackQuery):
            await source.message.edit_text(
                success_msg,
                parse_mode="HTML",
                reply_markup=get_shop_menu()
            )
        else:
            await source.answer(success_msg, parse_mode="HTML")

        await state.clear()

    except ValueError as e:
        error_msg = f"❌ {str(e)}\n\nПопробуйте позже или обратитесь в поддержку."
        if isinstance(source, CallbackQuery):
            await source.message.edit_text(error_msg, reply_markup=get_shop_menu())
        else:
            await source.answer(error_msg)
        await state.clear()

    except Exception as e:
        logger.error(f"Error creating order: {e}", exc_info=True)
        error_msg = "❌ Произошла ошибка при создании заказа. Попробуйте позже."
        if isinstance(source, CallbackQuery):
            await source.message.edit_text(error_msg, reply_markup=get_shop_menu())
        else:
            await source.answer(error_msg)
        await state.clear()

# Helper function to get shop menu keyboard
def get_shop_menu():
    from ..keyboards import shop_menu_keyboard
    return shop_menu_keyboard()

# Import logging at the end to avoid circular imports
import logging
logger = logging.getLogger(__name__)
