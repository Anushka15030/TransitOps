from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken
from app.repositories.base_repository import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, db: Session):
        super().__init__(RefreshToken, db)

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        return (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token_hash == token_hash)
            .first()
        )

    def revoke(self, token: RefreshToken) -> None:
        token.is_revoked = True
        token.revoked_at = datetime.now(timezone.utc)
        self.db.flush()

    def revoke_all_for_user(self, user_id) -> None:
        """Used for a 'logout everywhere' / security-incident scenario."""
        self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id, RefreshToken.is_revoked.is_(False)
        ).update({"is_revoked": True, "revoked_at": datetime.now(timezone.utc)})
        self.db.flush()