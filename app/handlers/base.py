from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from ..database import get_session, User
from ..keyboards import main_menu_keyboard

router = Router()

@router.message(CommandStart())
async def start_cmd(message: Message):
    async for session in get_session():
        # Создаем пользователя при первом запуске
        user = await session.get(User, message.from_user.id)
        if not user:
            user = User(telegram_id=message.from_user.id)
            session.add(user)
            await session.commit()

    await message.answer(
        "Добро пожаловать в галерею искусства! 🎨\n\nВыберите действие:",
        reply_markup=main_menu_keyboard()
    )

@router.message(Command("menu"))
async def menu_cmd(message: Message):
    await message.answer("Главное меню:", reply_markup=main_menu_keyboard())

@router.callback_query(F.data == "main_menu")
async def main_menu(query: CallbackQuery):
    await query.message.edit_text(
        "Главное меню:",
        reply_markup=main_menu_keyboard()
    )
