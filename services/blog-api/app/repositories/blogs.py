"""All SQL that touches the blogs table lives here."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Blog


def list_recent(db: Session, *, limit: int, offset: int) -> Sequence[Blog]:
    stmt = select(Blog).order_by(Blog.created_at.desc(), Blog.id.desc()).limit(limit).offset(offset)
    return db.scalars(stmt).all()


def get(db: Session, blog_id: int) -> Blog | None:
    return db.get(Blog, blog_id)


def create(db: Session, *, title: str, body: str, author_id: int) -> Blog:
    blog = Blog(title=title, body=body, author_id=author_id)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


def delete(db: Session, blog: Blog) -> None:
    db.delete(blog)
    db.commit()
