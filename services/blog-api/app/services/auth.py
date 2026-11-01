from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.repositories import users as users_repo
from app.schemas import UserCreate
from app.services.errors import Conflict, Unauthorized

# Spend the same bcrypt time whether or not the username exists, so response
# timing doesn't reveal which usernames are registered.
_DUMMY_HASH = hash_password("timing-equaliser-not-a-real-password")


def register(db: Session, data: UserCreate) -> User:
    if users_repo.exists_with(db, username=data.username, email=data.email):
        raise Conflict("username or email is already registered")
    try:
        return users_repo.create(
            db,
            name=data.name,
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
        )
    except IntegrityError as exc:  # two sign-ups racing for the same username
        db.rollback()
        raise Conflict("username or email is already registered") from exc


def login(db: Session, username: str, password: str) -> tuple[str, User]:
    user = users_repo.get_by_username(db, username)
    if user is None:
        verify_password(password, _DUMMY_HASH)
        raise Unauthorized("invalid username or password")
    if not verify_password(password, user.password_hash):
        raise Unauthorized("invalid username or password")
    return create_access_token(user.id), user
