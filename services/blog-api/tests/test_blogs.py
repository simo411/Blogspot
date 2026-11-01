from tests.conftest import login_headers


def create_blog(client, headers, title="Hello", body="First post\nsecond line"):
    return client.post("/api/blogs", json={"title": title, "body": body}, headers=headers)


def test_anyone_can_read_blogs(client):
    headers = login_headers(client, "smriti")
    created = create_blog(client, headers).json()

    listing = client.get("/api/blogs")
    assert listing.status_code == 200
    assert [b["id"] for b in listing.json()] == [created["id"]]

    one = client.get(f"/api/blogs/{created['id']}")
    assert one.status_code == 200
    assert one.json()["author"]["username"] == "smriti"
    assert "email" not in one.json()["author"]  # authors' emails stay private


def test_create_requires_login(client):
    assert client.post("/api/blogs", json={"title": "x", "body": "y"}).status_code == 401


def test_author_comes_from_token_not_body(client):
    headers = login_headers(client, "smriti")
    res = client.post(
        "/api/blogs",
        json={"title": "t", "body": "b", "author_id": 999, "author": "Someone else"},
        headers=headers,
    )
    assert res.status_code == 201
    assert res.json()["author"]["username"] == "smriti"


def test_only_author_can_delete(client):
    owner = login_headers(client, "smriti")
    other = login_headers(client, "intruder")
    blog_id = create_blog(client, owner).json()["id"]

    assert client.delete(f"/api/blogs/{blog_id}").status_code == 401
    assert client.delete(f"/api/blogs/{blog_id}", headers=other).status_code == 403
    assert client.delete(f"/api/blogs/{blog_id}", headers=owner).status_code == 204
    assert client.get(f"/api/blogs/{blog_id}").status_code == 404


def test_missing_blog_is_404(client):
    assert client.get("/api/blogs/12345").status_code == 404


def test_newest_first_and_pagination(client):
    headers = login_headers(client, "smriti")
    ids = [create_blog(client, headers, title=f"post {i}").json()["id"] for i in range(3)]

    listing = client.get("/api/blogs").json()
    assert [b["id"] for b in listing] == list(reversed(ids))

    page = client.get("/api/blogs", params={"limit": 1, "offset": 1}).json()
    assert [b["id"] for b in page] == [ids[1]]


def test_validation(client):
    headers = login_headers(client, "smriti")
    assert create_blog(client, headers, title="").status_code == 422
    assert client.get("/api/blogs", params={"limit": 1000}).status_code == 422
