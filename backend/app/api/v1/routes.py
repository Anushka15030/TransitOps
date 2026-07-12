from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_permission
from app.core.permissions import Permission
from app.repositories.route_repository import RouteRepository
from app.schemas.route_schema import RouteOptionResponse

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.get(
    "/options",
    response_model=list[RouteOptionResponse],
    dependencies=[Depends(require_permission(Permission.ROUTE_READ))],
)
def list_route_options(db: Session = Depends(get_db)):
    """Lightweight dropdown source for trip creation. Full CRUD pending."""
    routes = RouteRepository(db).list_active()
    return [RouteOptionResponse.model_validate(r) for r in routes]