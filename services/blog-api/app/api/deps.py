from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import User
from app.repositories import users as users_repo
from app.services.errors import Unauthorized

# HTTPBearer also adds the "Authorize" button to the Swagger UI at /api/docs.
bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> User:
    if credentials is None:
        raise Unauthorized("not authenticated")
    user_id = decode_access_token(credentials.credentials)
    user = users_repo.get_by_id(db, user_id) if user_id is not None else None
    if user is None:
        raise Unauthorized("invalid or expired token")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
