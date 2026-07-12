from sqlalchemy.orm import Session

from app.models.role import Role
from app.repositories.base_repository import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: Session):
        super().__init__(Role, db)

    def get_by_name(self, name: str) -> Role | None:
        return self.db.query(Role).filter(Role.name == name).first()