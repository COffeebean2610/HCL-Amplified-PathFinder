import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from app.config import settings


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    bcrypt has a 72-byte password limit.
    Validation is handled by the Pydantic schema,
    but we also protect this function directly.
    """
    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError("Password must be 72 bytes or fewer")

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.
    """
    try:
        plain_bytes = plain.encode("utf-8")

        if len(plain_bytes) > 72:
            return False

        hashed_bytes = hashed.encode("utf-8")

        return bcrypt.checkpw(
            plain_bytes,
            hashed_bytes,
        )

    except (ValueError, TypeError, bcrypt.exceptions.BcryptError):
        return False


def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(
        minutes=settings.jwt_expire_minutes
    )

    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> Optional[str]:
    """
    Returns user_id (sub) or None on failure.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )

        return payload.get("sub")

    except JWTError:
        return None