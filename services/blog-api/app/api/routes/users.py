from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.repositories import users as users_repo
from app.schemas import AvatarUpdate, UserMe

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserMe)
def read_me(user: CurrentUser):
    return user


@router.patch("/me/avatar", response_model=UserMe)
def update_my_avatar(data: AvatarUpdate, user: CurrentUser, db: DbSession):
    # v1 let anyone change anyone's avatar via /update-avatar/:userId.
    # Now the user is whoever the token says, so you can only change your own.
    return users_repo.set_avatar(db, user, data.avatar)
