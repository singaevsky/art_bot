from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from ..keyboards import shop_menu_keyboard, gallery_keyboard
from ..database import get_session
from ..services.orders import create_order
from ..states import OrderCreate

router = Router()

# Пример данных галереи
GALLERY_ITEMS = {
    "painting_1": {"name": "Абстрактная картина", "price": 5000},
    "sculpture_1": {"name": "Бронзовая скульптура", "price": 15000}
}

@router.callback_query(F.data == "shop")
async def shop_handler(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text(
        "🛍 <b>Магазин искусства</b>\n\nВыберите раздел:",
        parse_mode="HTML",
        reply_markup=shop_menu_keyboard()
    )

@router.callback_query(F.data.startswith("gallery_"))
async def gallery_handler(query: CallbackQuery, state: FSMContext):
    page = int(query.data.split("_")[1])
    await query.message.edit_text(
        "🎨 <b>Галерея</b>\n\nВыберите произведение:",
        parse_mode="HTML",
        reply_markup=gallery_keyboard(page)
    )

@router.callback_query(F.data.startswith("item_"))
async def item_handler(query: CallbackQuery, state: FSMContext):
    item_id = query.data.split("_", 1)[1]
    await state.set_state(OrderCreate.choose_item)
    await state.update_data(item_id=item_id)

    if item_id in GALLERY_ITEMS:
        item = GALLERY_ITEMS[item_id]
        await query.message.edit_text(
            f"🎨 <b>{item['name']}</b>\n\n💰 {item['price']} руб.\n\n"
            "Выберите действие:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton("🛒 Выбрать для покупки", callback_data="select_item")],
                [InlineKeyboardButton("⬅️ Назад к галерее", callback_data="gallery_0")],
                [InlineKeyboardButton("🛍 Назад в магазин", callback_data="shop")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
        )

# Дополнительные обработчики для процесса покупки...
