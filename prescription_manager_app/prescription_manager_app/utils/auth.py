import bcrypt
from typing import Optional

# Tune to your environment (higher = slower/stronger)
BCRYPT_ROUNDS = 12


def hash_password_bcrypt(raw_password: str) -> str:
    """Return bcrypt hash string for storage."""
    if not isinstance(raw_password, str):
        raise TypeError("raw_password must be a string")
    hashed = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt(rounds=BCRYPT_ROUNDS))
    return hashed.decode("utf-8")


def verify_bcrypt(raw_password: str, stored_hash: str) -> bool:
    """Verify raw password against bcrypt hash. Safe for malformed values."""
    try:
        if not isinstance(stored_hash, str):
            return False
        return bcrypt.checkpw(raw_password.encode("utf-8"), stored_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def is_bcrypt_hash(stored_hash: Optional[str]) -> bool:
    """Detect bcrypt-style hashes ($2b$, $2a$, $2y$)."""
    if not isinstance(stored_hash, str):
        return False
    return stored_hash.startswith(("$2b$", "$2a$", "$2y$"))


def verify_password(raw_password: str, stored_hash: str) -> bool:
    """
    Verify a password assuming stored_hash is a bcrypt hash.
    Returns True on success, False otherwise.
    """
    if not is_bcrypt_hash(stored_hash):
        # We accept only bcrypt hashes in this codepath.
        return False
    return verify_bcrypt(raw_password, stored_hash)
