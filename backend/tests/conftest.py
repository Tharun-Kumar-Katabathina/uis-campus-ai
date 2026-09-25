import pytest

from app.core.config import settings


@pytest.fixture(autouse=True)
def _test_jwt_secret():
    """app/core/config.py deliberately defaults JWT_SECRET to "" so a
    forgotten production secret fails loudly rather than silently signing
    tokens with an empty/weak key. Tests need a real value to exercise
    the signing path."""
    original = settings.jwt_secret
    settings.jwt_secret = "test-secret-for-ci-only-32-bytes+"
    yield
    settings.jwt_secret = original
