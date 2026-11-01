from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# A pool instead of v1's single connection: pre_ping drops dead connections
# (MySQL restarts, idle timeouts) instead of crashing the request.
_engine_kwargs: dict = {"pool_pre_ping": True}
if settings.sqlalchemy_url.get_backend_name() == "mysql":
    _engine_kwargs.update(pool_size=5, max_overflow=10, pool_recycle=280)
elif settings.sqlalchemy_url.get_backend_name() == "sqlite":
    _engine_kwargs.update(connect_args={"check_same_thread": False})

engine = create_engine(settings.sqlalchemy_url, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
