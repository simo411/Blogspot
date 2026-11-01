"""All SQL that touches the users table lives here."""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import User


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def exists_with(db: Session, *, username: str, email: str) -> bool:
    stmt = select(User.id).where(or_(User.username == username, User.email == email)).limit(1)
    return db.scalar(stmt) is not None


def create(db: Session, *, name: str, username: str, email: str, password_hash: str) -> User:
    user = User(name=name, username=username, email=email, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_avatar(db: Session, user: User, avatar: int) -> User:
    user.avatar = avatar
    db.commit()
    db.refresh(user)
    return user
