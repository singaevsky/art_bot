from aiogram.fsm.state import State, StatesGroup

class OrderCreate(StatesGroup):
    """States for order creation flow."""
    choose_item = State()
    choose_payment = State()
    choose_delivery = State()
    input_address = State()
    confirm_order = State()

class Admin(StatesGroup):
    """States for admin actions."""
    waiting_for_order_id = State()
    waiting_for_new_status = State()
    waiting_for_comment = State()

class Feedback(StatesGroup):
    """States for feedback collection."""
    waiting_for_message = State()
