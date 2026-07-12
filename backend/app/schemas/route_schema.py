import uuid

from app.schemas.base_schema import BaseSchema


class RouteOptionResponse(BaseSchema):
    id: uuid.UUID
    name: str
    origin: str
    destination: str