from typing import Dict, List, Optional
from ..config import settings

# Default gallery items (can be loaded from database in future)
DEFAULT_GALLERY_ITEMS = {
    "painting_1": {
        "name": "Абстрактная картина",
        "price": 5000,
        "description": "Красочная абстрактная картина маслом",
        "type": "картина",
        "image_url": "https://example.com/painting1.jpg"
    },
    "sculpture_1": {
        "name": "Бронзовая скульптура",
        "price": 15000,
        "description": "Скульптура в бронзе современного художника",
        "type": "скульптура",
        "image_url": "https://example.com/sculpture1.jpg"
    },
    "painting_2": {
        "name": "Пейзажное полотно",
        "price": 8000,
        "description": "Красивый пейзаж маслом",
        "type": "картина",
        "image_url": "https://example.com/painting2.jpg"
    }
}

PAYMENT_METHODS = {
    "card": "Банковская карта",
    "sbp": "СБП (Система быстрых платежей)",
    "cash": "Наличные при получении"
}

DELIVERY_METHODS = {
    "pickup": "Самовывоз",
    "delivery": "Доставка по адресу"
}

class GalleryService:
    """Service for gallery operations."""

    @staticmethod
    def get_items(page: int = 0, per_page: int = settings.ITEMS_PER_PAGE) -> List[tuple]:
        """Get paginated gallery items."""
        items = list(DEFAULT_GALLERY_ITEMS.items())
        start_idx = page * per_page
        end_idx = start_idx + per_page
        return items[start_idx:end_idx]

    @staticmethod
    def get_item(item_id: str) -> Optional[Dict]:
        """Get item by ID."""
        return DEFAULT_GALLERY_ITEMS.get(item_id)

    @staticmethod
    def has_next_page(page: int, total_items: int = None) -> bool:
        """Check if there is next page."""
        if total_items is None:
            total_items = len(DEFAULT_GALLERY_ITEMS)
        return (page + 1) * settings.ITEMS_PER_PAGE < total_items

    @staticmethod
    def has_previous_page(page: int) -> bool:
        """Check if there is previous page."""
        return page > 0
