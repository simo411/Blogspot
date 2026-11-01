"""Block until the database accepts connections (or give up).

Compose already waits for the MySQL healthcheck, but in Kubernetes the Job can start
before MySQL is ready, so the service waits for itself instead of relying on ordering.
"""

import os
import sys
import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from migrations.db_url import database_url

TIMEOUT = int(os.environ.get("DB_WAIT_TIMEOUT", "120"))


def main() -> int:
    engine = create_engine(database_url())
    deadline = time.monotonic() + TIMEOUT
    attempt = 0
    while True:
        attempt += 1
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"database is reachable (attempt {attempt})", flush=True)
            return 0
        except OperationalError as exc:
            if time.monotonic() > deadline:
                print(f"database not reachable after {TIMEOUT}s: {exc.orig}", file=sys.stderr)
                return 1
            print(f"waiting for database (attempt {attempt})...", flush=True)
            time.sleep(2)


if __name__ == "__main__":
    sys.exit(main())
