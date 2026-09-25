from enum import StrEnum

from pydantic import BaseModel


class Role(StrEnum):
    STUDENT = "student"
    FACULTY = "faculty"
    STAFF = "staff"
    ADMIN = "admin"


class User(BaseModel):
    user_id: str
    role: Role
