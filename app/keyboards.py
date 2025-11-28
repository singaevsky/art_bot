from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Optional

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("📝 Подписаться", callback_data="subscribe")],
        [InlineKeyboardButton("✅ Проверить статус", callback_data="check")],
        [InlineKeyboardButton("🎁 Получить подарок", callback_data="gift")],
        [InlineKeyboardButton("🛍 Перейти к покупкам", callback_data="shop")],
        [InlineKeyboardButton("❌ Отписаться", callback_data="unsubscribe")]
    ])

def shop_menu_keyboard() -> InlineKeyboardMarkup:
    """Shop menu keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🎨 Галерея", callback_data="gallery_0")],
        [InlineKeyboardButton("📦 Мои покупки", callback_data="my_purchases")],
        [InlineKeyboardButton("💳 Способ оплаты", callback_data="payment_methods")],
        [InlineKeyboardButton("🚚 Способ получения", callback_data="delivery_methods")],
        [InlineKeyboardButton("❓ FAQ", callback_data="faq")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])

def gallery_keyboard(page: int = 0, has_next: bool = False, has_prev: bool = False) -> InlineKeyboardMarkup:
    """Gallery keyboard with pagination."""
    buttons = []

    # Item buttons would be added dynamically in handler
    navigation = []
    if has_prev:
        navigation.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"gallery_{page-1}"))
    if has_next:
        navigation.append(InlineKeyboardButton("➡️ Вперед", callback_data=f"gallery_{page+1}"))

    if navigation:
        buttons.append(navigation)

    buttons.extend([
        [InlineKeyboardButton("🛍 Назад в магазин", callback_data="shop")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def item_keyboard(item_id: str) -> InlineKeyboardMarkup:
    """Individual item keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🛒 Выбрать для покупки", callback_data=f"select_item_{item_id}")],
        [InlineKeyboardButton("⬅️ Назад к галерее", callback_data="gallery_0")],
        [InlineKeyboardButton("🛍 Назад в магазин", callback_data="shop")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])

def payment_methods_keyboard(selected_item: Optional[str] = None) -> InlineKeyboardMarkup:
    """Payment methods keyboard."""
    buttons = [
        [InlineKeyboardButton("💳 Банковская карта", callback_data=f"pay_card{'_' + selected_item if selected_item else ''}")],
        [InlineKeyboardButton("⚡ СБП (Система быстрых платежей)", callback_data=f"pay_sbp{'_' + selected_item if selected_item else ''}")],
        [InlineKeyboardButton("💵 Наличные при получении", callback_data=f"pay_cash{'_' + selected_item if selected_item else ''}")]
    ]

    if selected_item:
        buttons.append([InlineKeyboardButton("⬅️ Назад к товару", callback_data=f"item_{selected_item}")])

    buttons.extend([
        [InlineKeyboardButton("🛍 Назад в магазин", callback_data="shop")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def delivery_methods_keyboard(selected_item: str, payment_method: str) -> InlineKeyboardMarkup:
    """Delivery methods keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🏪 Самовывоз", callback_data=f"deliver_pickup_{payment_method}_{selected_item}")],
        [InlineKeyboardButton("🚚 Доставка по адресу", callback_data=f"deliver_delivery_{payment_method}_{selected_item}")],
        [InlineKeyboardButton("⬅️ Назад к оплате", callback_data=f"pay_{payment_method}_{selected_item}")],
        [InlineKeyboardButton("🛍 Назад в магазин", callback_data="shop")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])

def confirm_order_keyboard(selected_item: str, payment_method: str, delivery_method: str) -> InlineKeyboardMarkup:
    """Order confirmation keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("✅ Подтвердить заказ", callback_data=f"confirm_order_{selected_item}_{payment_method}_{delivery_method}")],
        [InlineKeyboardButton("❌ Отменить", callback_data=f"item_{selected_item}")]
    ])

def admin_orders_keyboard(orders: List[tuple]) -> InlineKeyboardMarkup:
    """Admin keyboard for order management."""
    buttons = []
    for order_id, item_name, status in orders:
        buttons.append([InlineKeyboardButton(
            f"#{order_id} {item_name[:20]}... ({status})",
            callback_data=f"admin_order_{order_id}"
        )])

    if buttons:
        buttons.append([InlineKeyboardButton("🔄 Обновить список", callback_data="admin_orders")])

    buttons.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def order_status_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Keyboard for changing order status."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("⏳ В обработке", callback_data=f"set_status_{order_id}_pending")],
        [InlineKeyboardButton("✅ Подтвержден", callback_data=f"set_status_{order_id}_confirmed")],
        [InlineKeyboardButton("🚚 Отправлен", callback_data=f"set_status_{order_id}_shipped")],
        [InlineKeyboardButton("📦 Доставлен", callback_data=f"set_status_{order_id}_delivered")],
        [InlineKeyboardButton("❌ Отменен", callback_data=f"set_status_{order_id}_cancelled")],
        [InlineKeyboardButton("⬅️ Назад к списку", callback_data="admin_orders")]
    ])

def contact_keyboard() -> ReplyKeyboardMarkup:
    """Contact request keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("📞 Отправить контакт", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
