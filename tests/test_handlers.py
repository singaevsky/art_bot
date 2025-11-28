"""
Tests for bot handlers.
"""

import pytest
from unittest.mock import AsyncMock, Mock
from aiogram.types import Message, CallbackQuery, User, Chat, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from app.handlers.base import start_cmd, menu_cmd, main_menu
from app.handlers.shop import shop_handler, gallery_handler, item_handler
from app.handlers.orders import payment_handler, delivery_handler, address_input
from app.states import OrderCreate

pytest_plugins = ('tests.conftest',)

class TestBaseHandlers:
    """Test basic handlers."""

    @pytest.mark.asyncio
    async def test_start_command(self):
        """Test /start command."""
        message = Mock(spec=Message)
        message.from_user = Mock(spec=User)
        message.from_user.id = 123456
        message.answer = AsyncMock()

        await start_cmd(message)

        message.answer.assert_called_once()
        args = message.answer.call_args
        assert "Добро пожаловать" in args[0][0]
        assert "reply_markup" in args[1]

    @pytest.mark.asyncio
    async def test_menu_command(self):
        """Test /menu command."""
        message = Mock(spec=Message)
        message.answer = AsyncMock()

        await menu_cmd(message)

        message.answer.assert_called_once()
        args = message.answer.call_args
        assert "Главное меню" in args[0][0]

    @pytest.mark.asyncio
    async def test_main_menu_callback(self):
        """Test main menu callback."""
        query = Mock(spec=CallbackQuery)
        query.message = Mock(spec=Message)
        query.message.edit_text = AsyncMock()

        await main_menu(query)

        query.message.edit_text.assert_called_once()
        args = query.message.edit_text.call_args
        assert "Главное меню" in args[0][0]

class TestShopHandlers:
    """Test shop handlers."""

    @pytest.mark.asyncio
    async def test_shop_handler(self):
        """Test shop menu handler."""
        query = Mock(spec=CallbackQuery)
        query.message = Mock(spec=Message)
        query.message.edit_text = AsyncMock()
        query.data = "shop"

        await shop_handler(query, Mock(spec=FSMContext))

        query.message.edit_text.assert_called_once()
        args = query.message.edit_text.call_args
        assert "🛍" in args[0][0]
        assert args[1]['parse_mode'] == 'HTML'

    @pytest.mark.asyncio
    async def test_gallery_handler(self):
        """Test gallery handler."""
        query = Mock(spec=CallbackQuery)
        query.message = Mock(spec=Message)
        query.message.edit_text = AsyncMock()
        query.data = "gallery_0"

        await gallery_handler(query, Mock(spec=FSMContext))

        query.message.edit_text.assert_called_once()
        args = query.message.edit_text.call_args
        assert "🎨" in args[0][0]

    @pytest.mark.asyncio
    async def test_item_handler(self):
        """Test item details handler."""
        query = Mock(spec=CallbackQuery)
        query.message = Mock(spec=Message)
        query.message.edit_text = AsyncMock()
        query.data = "item_painting_1"

        state = Mock(spec=FSMContext)
        state.set_state = AsyncMock()
        state.update_data = AsyncMock()

        await item_handler(query, state)

        state.set_state.assert_called_once_with(OrderCreate.choose_item)
        query.message.edit_text.assert_called_once()
        args = query.message.edit_text.call_args
        assert "💰" in args[0][0]

class TestOrderHandlers:
    """Test order handlers."""

    @pytest.mark.asyncio
    async def test_payment_handler(self):
        """Test payment method selection."""
        query = Mock(spec=CallbackQuery)
        query.message = Mock(spec=Message)
        query.message.edit_text = AsyncMock()
        query.data = "pay_card"

        state = Mock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await payment_handler(query, state)

        state.update_data.assert_called_once()
        state.set_state.assert_called_once_with(OrderCreate.choose_delivery)
        query.message.edit_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_delivery_handler_pickup(self):
        """Test delivery method selection - pickup."""
        query = Mock(spec=CallbackQuery)
        query.message = Mock(spec=Message)
        query.message.edit_text = AsyncMock()
        query.data = "deliver_pickup_card_painting_1"

        state = Mock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={
            'item_id': 'painting_1',
            'payment_method': 'card'
        })

        # Mock the finalize_order function
        with pytest.patch('app.handlers.orders.finalize_order') as mock_finalize:
            await delivery_handler(query, state)

            mock_finalize.assert_called_once()
            args = mock_finalize.call_args[0]
            assert args[0] == query  # source
            assert args[1] == state  # state
            assert args[2] is None   # address

    @pytest.mark.asyncio
    async def test_delivery_handler_delivery(self):
        """Test delivery method selection - delivery address."""
        query = Mock(spec=CallbackQuery)
        query.message = Mock(spec=Message)
        query.message.edit_text = AsyncMock()
        query.data = "deliver_delivery_card_painting_1"

        state = Mock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={
            'item_id': 'painting_1',
            'payment_method': 'card'
        })
        state.set_state = AsyncMock()
        state.update_data = AsyncMock()

        await delivery_handler(query, state)

        state.update_data.assert_called_once()
        state.set_state.assert_called_once_with(OrderCreate.input_address)
        query.message.edit_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_address_input_valid(self):
        """Test address input with valid address."""
        message = Mock(spec=Message)
        message.from_user = Mock(spec=User)
        message.from_user.id = 123456
        message.text = "г. Москва, ул. Тверская, д. 1, кв. 1"
        message.answer = AsyncMock()

        state = Mock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={
            'item_id': 'painting_1',
            'payment_method': 'card',
            'delivery_method': 'delivery'
        })
        state.clear = AsyncMock()

        # Mock the finalize_order function
        with pytest.patch('app.handlers.orders.finalize_order') as mock_finalize:
            await address_input(message, state)

            mock_finalize.assert_called_once()
            args = mock_finalize.call_args[0]
            assert args[2] == message.text  # address

    @pytest.mark.asyncio
    async def test_address_input_invalid(self):
        """Test address input with invalid address."""
        message = Mock(spec=Message)
        message.text = "abc"
        message.answer = AsyncMock()

        state = Mock(spec=FSMContext)

        await address_input(message, state)

        message.answer.assert_called_once()
        assert "слишком короткий" in message.answer.call_args[0][0]

class TestAdminHandlers:
    """Test admin handlers."""

    @pytest.mark.asyncio
    async def test_admin_command_access_denied(self):
        """Test admin command with no access."""
        message = Mock(spec=Message)
        message.from_user = Mock(spec=User)
        message.from_user.id = 999999
        message.answer = AsyncMock()

        with pytest.patch('app.config.settings.ADMIN_IDS', [123456]):
            # Import admin handlers after patching config
            from app.handlers.admin import admin_cmd
            await admin_cmd(message)

            message.answer.assert_called_once()
            assert "нет доступа" in message.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_admin_command_access_granted(self):
        """Test admin command with access."""
        message = Mock(spec=Message)
        message.from_user = Mock(spec=User)
        message.from_user.id = 123456
        message.answer = AsyncMock()

        state = Mock(spec=FSMContext)
        state.set_state = AsyncMock()

        with pytest.patch('app.config.settings.ADMIN_IDS', [123456]):
            from app.handlers.admin import admin_cmd
            await admin_cmd(message, state)

            message.answer.assert_called_once()
            assert "админ-панель" in message.answer.call_args[0][0]
            state.set_state.assert_called_once()

class TestValidation:
    """Test validation functions."""

    def test_validate_address_valid(self):
        """Test address validation - valid address."""
        from app.utils.validators import validate_address

        is_valid, sanitized = validate_address("г. Москва, ул. Тверская, д. 1, кв. 1")
        assert is_valid is True
        assert len(sanitized) >= 10

    def test_validate_address_invalid(self):
        """Test address validation - invalid address."""
        from app.utils.validators import validate_address

        is_valid, _ = validate_address("abc")
        assert is_valid is False

    def test_validate_phone_valid(self):
        """Test phone validation - valid phone."""
        from app.utils.validators import validate_phone

        is_valid, sanitized = validate_phone("+7 (999) 123-45-67")
        assert is_valid is True
        assert sanitized.startswith("+7")

    def test_sanitize_input(self):
        """Test input sanitization."""
        from app.utils.validators import sanitize_input

        result = sanitize_input("<script>alert('test')</script>Hello")
        assert "<script>" not in result
        assert "Hello" in result

    def test_format_price(self):
        """Test price formatting."""
        from app.utils.validators import format_price

        result = format_price(5000)
        assert "5 000" in result or "5000" in result
        assert "₽" in result
