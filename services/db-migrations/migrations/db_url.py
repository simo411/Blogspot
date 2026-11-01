"""Build the SQLAlchemy URL from environment variables.

DATABASE_URL wins if set (handy for tests, e.g. sqlite:///./test.db).
Otherwise the URL is assembled from DB_HOST / DB_PORT / DB_USER / DB_PASSWORD / DB_NAME,
which is how compose and Kubernetes inject config and secrets.
"""

import os

from sqlalchemy.engine import URL, make_url


def database_url() -> URL:
    if os.environ.get("DATABASE_URL"):
        return make_url(os.environ["DATABASE_URL"])
    return URL.create(
        "mysql+pymysql",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "3306")),
        database=os.environ["DB_NAME"],
        query={"charset": "utf8mb4"},
    )
