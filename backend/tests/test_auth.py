from datetime import timedelta

import jwt
import pytest

from app.core.auth import ALGORITHM, create_access_token, decode_access_token
from app.core.config import settings
from app.models.user import Role, User


def test_create_and_decode_access_token_round_trips():
    token = create_access_token("user-1", Role.STUDENT)

    user = decode_access_token(token)

    assert user == User(user_id="user-1", role=Role.STUDENT)


def test_decode_rejects_expired_token():
    token = create_access_token("user-1", Role.STUDENT, expires_delta=timedelta(seconds=-1))

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_decode_rejects_bad_signature():
    token = create_access_token("user-1", Role.STUDENT)
    tampered = jwt.encode(
        jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM]),
        "a completely different secret",
        algorithm=ALGORITHM,
    )

    with pytest.raises(jwt.InvalidSignatureError):
        decode_access_token(tampered)


def test_decode_rejects_unrecognized_role():
    payload = {"sub": "user-1", "role": "superuser"}
    token = jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)

    with pytest.raises(ValueError):
        decode_access_token(token)
