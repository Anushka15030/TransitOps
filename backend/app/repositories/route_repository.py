from sqlalchemy.orm import Session

from app.models.enums import RouteStatus
from app.models.route import Route
from app.repositories.base_repository import BaseRepository


class RouteRepository(BaseRepository[Route]):
    def __init__(self, db: Session):
        super().__init__(Route, db)

    def list_active(self) -> list[Route]:
        return self.db.query(Route).filter(Route.status == RouteStatus.ACTIVE).order_by(Route.name).all()