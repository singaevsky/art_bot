import re
from typing import Optional, Tuple

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS and injection."""
    if not text:
        return ""

    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32)
    # Strip whitespace
    text = text.strip()

    return text[:500]  # Limit length

def validate_address(address: str) -> Tuple[bool, str]:
    """
    Validate delivery address.
    Returns (is_valid, sanitized_address).
    """
    if not address or len(address.strip()) < 10:
        return False, "Адрес слишком короткий"

    if len(address) > 200:
        return False, "Адрес слишком длинный"

    # Check for suspicious patterns
    suspicious_patterns = [
        r'<script',
        r'javascript:',
        r'data:',
        r'vbscript:'
    ]

    address_lower = address.lower()
    for pattern in suspicious_patterns:
        if re.search(pattern, address_lower):
            return False, "Недопустимые символы в адресе"

    return True, sanitize_input(address)

def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validate phone number.
    Returns (is_valid, sanitized_phone).
    """
    if not phone:
        return False, "Номер телефона не указан"

    # Remove all non-digit characters except +
    clean_phone = re.sub(r'[^\d+]', '', phone)

    # Basic validation
    if len(clean_phone) < 10:
        return False, "Номер телефона слишком короткий"

    if len(clean_phone) > 15:
        return False, "Номер телефона слишком длинный"

    # Check for country code
    if not clean_phone.startswith('+'):
        # Add Russian country code if not present
        clean_phone = '+7' + clean_phone.lstrip('8')

    return True, clean_phone

def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email address.
    Returns (is_valid, sanitized_email).
    """
    if not email:
        return True, ""  # Email is optional

    email = email.strip().lower()

    # Basic email regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(email_pattern, email):
        return False, "Некорректный формат email"

    return True, email

def format_price(price: int) -> str:
    """Format price with ruble sign."""
    return f"{price:,} ₽".replace(",", " ")

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
