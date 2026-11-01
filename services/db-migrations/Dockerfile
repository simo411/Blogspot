# One-shot schema service: waits for MySQL, runs `alembic upgrade head`, exits.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY alembic.ini wait_for_db.py entrypoint.sh ./
COPY migrations ./migrations

RUN chmod +x entrypoint.sh \
 && useradd --system --uid 10001 --no-create-home migrator
USER 10001

ENTRYPOINT ["./entrypoint.sh"]
