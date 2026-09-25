from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.models.user import Role, User

ALGORITHM = "HS256"
DEFAULT_EXPIRY = timedelta(hours=24)

_bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(user_id: str, role: Role, expires_delta: timedelta = DEFAULT_EXPIRY) -> str:
    payload = {
        "sub": user_id,
        "role": role.value,
        "exp": datetime.now(UTC) + expires_delta,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> User:
    """Raises jwt.PyJWTError (expired, malformed, bad signature, ...) or
    ValueError (unrecognized role) on any invalid token."""
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    return User(user_id=payload["sub"], role=Role(payload["role"]))


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return decode_access_token(credentials.credentials)
    except (jwt.PyJWTError, ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
