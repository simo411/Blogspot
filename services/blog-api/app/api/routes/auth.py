from fastapi import APIRouter, status

from app.api.deps import DbSession
from app.schemas import LoginRequest, TokenResponse, UserCreate, UserMe
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserMe, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: DbSession):
    return auth_service.register(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: DbSession):
    token, user = auth_service.login(db, data.username, data.password)
    return TokenResponse(access_token=token, user=UserMe.model_validate(user))
