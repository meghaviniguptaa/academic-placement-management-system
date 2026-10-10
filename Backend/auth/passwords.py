
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)


def hash_password(password: str) -> str:
    """Hash a password before storing it."""
    if not isinstance(password, str) or not password:
        raise ValueError("Password must not be empty.")

    return generate_password_hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify an entered password against its stored hash."""
    if not isinstance(password, str) or not isinstance(stored_hash, str):
        return False

    try:
        return check_password_hash(stored_hash, password)
    except (ValueError, TypeError):
        return False
