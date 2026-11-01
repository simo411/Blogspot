"""Probes used by Docker healthchecks and Kubernetes.

/healthz  liveness:  the process is up. No DB call, so a DB outage doesn't make
                     Kubernetes restart every API pod in a loop.
/readyz   readiness: the DB is reachable AND the schema has been migrated.
                     Until db-migrations has run, the pod gets no traffic.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import DbSession

router = APIRouter(tags=["health"])


@router.get("/healthz")
def liveness():
    return {"status": "ok"}


@router.get("/readyz")
def readiness(db: DbSession):
    try:
        version = db.execute(text("SELECT version_num FROM alembic_version")).scalar()
    except SQLAlchemyError:
        return JSONResponse({"status": "unavailable", "reason": "database unreachable or not migrated"}, 503)
    if version is None:
        return JSONResponse({"status": "unavailable", "reason": "schema not migrated"}, 503)
    return {"status": "ready", "schema_version": version}
