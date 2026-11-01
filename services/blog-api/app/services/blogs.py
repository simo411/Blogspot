from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.models import Blog, User
from app.repositories import blogs as blogs_repo
from app.schemas import BlogCreate
from app.services.errors import Forbidden, NotFound


def list_blogs(db: Session, *, limit: int, offset: int) -> Sequence[Blog]:
    return blogs_repo.list_recent(db, limit=limit, offset=offset)


def get_blog(db: Session, blog_id: int) -> Blog:
    blog = blogs_repo.get(db, blog_id)
    if blog is None:
        raise NotFound("blog not found")
    return blog


def create_blog(db: Session, data: BlogCreate, author: User) -> Blog:
    # The author comes from the verified token, never from the request body.
    return blogs_repo.create(db, title=data.title, body=data.body, author_id=author.id)


def delete_blog(db: Session, blog_id: int, current_user: User) -> None:
    blog = get_blog(db, blog_id)
    # Enforced on the server: in v1 only the React UI hid the delete button.
    if blog.author_id != current_user.id:
        raise Forbidden("you can only delete your own blogs")
    blogs_repo.delete(db, blog)
