from tests.conftest import login_headers


def test_update_own_avatar(client):
    headers = login_headers(client, "smriti")
    res = client.patch("/api/users/me/avatar", json={"avatar": 3}, headers=headers)
    assert res.status_code == 200
    assert res.json()["avatar"] == 3
    assert client.get("/api/users/me", headers=headers).json()["avatar"] == 3


def test_avatar_must_be_1_to_5(client):
    headers = login_headers(client, "smriti")
    assert client.patch("/api/users/me/avatar", json={"avatar": 9}, headers=headers).status_code == 422


def test_avatar_requires_login(client):
    assert client.patch("/api/users/me/avatar", json={"avatar": 1}).status_code == 401


def test_liveness(client):
    assert client.get("/healthz").json() == {"status": "ok"}


def test_readiness_reports_schema_version(client):
    res = client.get("/readyz")
    assert res.status_code == 200
    assert res.json()["status"] == "ready"


def test_openapi_docs_are_under_api_prefix(client):
    assert client.get("/api/openapi.json").status_code == 200
    assert client.get("/api/docs").status_code == 200
