"""All configuration comes from environment variables (12-factor).

Compose passes them from .env; Kubernetes from a ConfigMap + Secret;
on AWS they can come from ECS task definitions or Secrets Manager. The code never changes.
"""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "blog-api"
    log_level: str = "info"

    # Either a full DATABASE_URL (tests, local tinkering) or the DB_* parts.
    database_url: str | None = None
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "blogspot"
    db_password: SecretStr = SecretStr("")
    db_name: str = "blogspot"

    # No default: the service refuses to start without a signing secret.
    jwt_secret: SecretStr = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # Only needed when the frontend is served from a different origin
    # (e.g. `npm start` on :3000 without the dev proxy). Comma-separated.
    cors_origins: str = ""

    @property
    def sqlalchemy_url(self) -> URL:
        if self.database_url:
            return make_url(self.database_url)
        return URL.create(
            "mysql+pymysql",
            username=self.db_user,
            password=self.db_password.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            query={"charset": "utf8mb4"},
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
