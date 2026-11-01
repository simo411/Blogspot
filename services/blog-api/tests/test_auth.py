from tests.conftest import login_headers, register


def test_register_returns_user_without_password(client):
    res = register(client, "smriti")
    assert res.status_code == 201
    body = res.json()
    assert body["username"] == "smriti"
    assert "password" not in body and "password_hash" not in body


def test_duplicate_username_or_email_is_409(client):
    register(client, "smriti")
    assert register(client, "smriti", email="other@example.com").status_code == 409
    assert register(client, "someone", email="smriti@example.com").status_code == 409


def test_register_validation(client):
    assert register(client, "ab").status_code == 422  # username too short
    assert register(client, "valid", password="short").status_code == 422
    assert register(client, "valid", password="é" * 40).status_code == 422  # > 72 bytes for bcrypt


def test_login_returns_token_and_user(client):
    register(client, "smriti")
    res = client.post("/api/auth/login", json={"username": "smriti", "password": "password123"})
    assert res.status_code == 200
    body = res.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["username"] == "smriti"
    assert "password_hash" not in body["user"]


def test_login_wrong_password_and_unknown_user_look_the_same(client):
    register(client, "smriti")
    wrong = client.post("/api/auth/login", json={"username": "smriti", "password": "nope-nope"})
    unknown = client.post("/api/auth/login", json={"username": "ghost", "password": "nope-nope"})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_me_requires_valid_token(client):
    assert client.get("/api/users/me").status_code == 401
    bad = client.get("/api/users/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert bad.status_code == 401

    headers = login_headers(client, "smriti")
    me = client.get("/api/users/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "smriti@example.com"
