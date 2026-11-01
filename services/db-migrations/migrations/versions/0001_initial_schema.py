"""Initial schema: users and blogs.

Replaces the v1 hand-made tables (members, blog_store):
- members  -> users  (password -> password_hash, avatar documented, unique username/email)
- blog_store -> blogs (author name is no longer duplicated; it is joined from users)

Revision ID: 0001
Revises:
Create Date: 2026-11-01
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

TABLE_OPTS = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
NOW = sa.text("CURRENT_TIMESTAMP")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("avatar", sa.SmallInteger, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=NOW),
        sa.UniqueConstraint("username", name="uq_users_username"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        **TABLE_OPTS,
    )

    op.create_table(
        "blogs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(200), nullable=False),
        # MEDIUMTEXT (16 MB) on MySQL; plain TEXT elsewhere (e.g. SQLite in tests).
        sa.Column("body", sa.Text().with_variant(mysql.MEDIUMTEXT(), "mysql"), nullable=False),
        sa.Column(
            "author_id",
            sa.Integer,
            sa.ForeignKey("users.id", name="fk_blogs_author_id_users", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=NOW),
        **TABLE_OPTS,
    )
    op.create_index("ix_blogs_author_id", "blogs", ["author_id"])
    op.create_index("ix_blogs_created_at", "blogs", ["created_at"])


def downgrade() -> None:
    # Dropping the tables drops their indexes too. (MySQL refuses to drop
    # ix_blogs_author_id on its own while the foreign key still needs it.)
    op.drop_table("blogs")
    op.drop_table("users")
