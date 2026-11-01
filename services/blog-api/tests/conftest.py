"""Test setup.

Default: a throwaway SQLite file, tables created from the ORM models.
CI / integration: set TEST_DATABASE_URL to a MySQL database already migrated by
services/db-migrations. Then the tests run against the real schema, which also
catches drift between the migrations and app/models.py.
"""

import os
import tempfile

_tmpdir = tempfile.mkdtemp()
_external_db = os.environ.get("TEST_DATABASE_URL")
os.environ["DATABASE_URL"] = _external_db or f"sqlite:///{_tmpdir}/test.db"
os.environ.setdefault("JWT_SECRET", "test-secret-test-secret-test-secret-123")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.db.session import engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base  # noqa: E402

if not _external_db:
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))
        conn.execute(text("INSERT INTO alembic_version VALUES ('test')"))


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM blogs"))
        conn.execute(text("DELETE FROM users"))


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def register(client: TestClient, username: str, password: str = "password123", **extra):
    payload = {
        "name": extra.get("name", username.title()),
        "username": username,
        "email": extra.get("email", f"{username}@example.com"),
        "password": password,
    }
    return client.post("/api/auth/register", json=payload)


def login_headers(client: TestClient, username: str, password: str = "password123") -> dict:
    register(client, username, password)
    res = client.post("/api/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}
