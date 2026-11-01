#!/bin/sh
# Default: wait for the DB, apply every pending migration, exit 0.
# Any arguments are passed straight to alembic instead, e.g.
#   docker compose run --rm db-migrations history
#   docker compose run --rm db-migrations downgrade -1
set -e

python wait_for_db.py

if [ "$#" -eq 0 ]; then
  alembic upgrade head
  echo "schema is at: $(alembic current 2>/dev/null | tail -1)"
else
  exec alembic "$@"
fi
