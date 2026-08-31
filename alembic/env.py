"""
Alembic migration environment — configured for async SQLAlchemy.

Key difference from default Alembic template: migrations run through
our async engine (asyncpg), not a sync one. Alembic's core migration
runner is still sync internally, so we bridge it using
run_sync() — this is the standard pattern for async SQLAlchemy + Alembic.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import settings
from app.db.base import Base
import app.models
from app.db.session import engine


# noqa: F401 — populates Base.metadata via app/models/__init__.py

# Alembic's config object — gives access to values in alembic.ini
config = context.config

# Wire our .env-driven DATABASE_URL into Alembic's config,
# overriding whatever (if anything) is in alembic.ini.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for logging (unchanged from default)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This is what powers `alembic revision --autogenerate` —
# Alembic compares this metadata against the live DB schema.
target_metadata = Base.metadata


def run_migrations_offline() -> None:

    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:

    connectable: AsyncEngine = engine

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
