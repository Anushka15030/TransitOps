from sqlalchemy.orm import Session, joinedload

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> User | None:
        return (
            self.db.query(User)
            .options(joinedload(User.role))
            .filter(User.email == email)
            .first()
        )

    def get_by_phone(self, phone: str) -> User | None:
        return self.db.query(User).filter(User.phone == phone).first()

    def exists_by_email_or_phone(self, email: str, phone: str) -> bool:
        return (
            self.db.query(User.id)
            .filter((User.email == email) | (User.phone == phone))
            .first()
            is not None
        )