import uuid
from datetime import datetime

from pydantic import EmailStr

from app.schemas.base_schema import BaseSchema


class UserResponse(BaseSchema):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    phone: str
    role: str
    is_active: bool
    created_at: datetime