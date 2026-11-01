from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas import BlogCreate, BlogOut
from app.services import blogs as blog_service

router = APIRouter(prefix="/blogs", tags=["blogs"])

BlogId = Annotated[int, Path(ge=1)]


@router.get("", response_model=list[BlogOut])
def list_blogs(
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return blog_service.list_blogs(db, limit=limit, offset=offset)


@router.get("/{blog_id}", response_model=BlogOut)
def get_blog(blog_id: BlogId, db: DbSession):
    return blog_service.get_blog(db, blog_id)


@router.post("", response_model=BlogOut, status_code=status.HTTP_201_CREATED)
def create_blog(data: BlogCreate, user: CurrentUser, db: DbSession):
    return blog_service.create_blog(db, data, user)


@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(blog_id: BlogId, user: CurrentUser, db: DbSession):
    blog_service.delete_blog(db, blog_id, user)
