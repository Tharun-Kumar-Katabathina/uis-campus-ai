from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/me")
def read_current_user(user: User = Depends(get_current_user)) -> User:
    return user
