"""
Generic CRUD repository. Every feature repository inherits this instead
of re-writing get/create/update/delete boilerplate — this is the concrete
mechanism behind "services never touch the DB directly."
"""

import uuid
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: uuid.UUID) -> ModelType | None:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        self.db.flush()   # get generated PK/defaults without committing yet
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelType) -> None:
        self.db.delete(obj)
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()