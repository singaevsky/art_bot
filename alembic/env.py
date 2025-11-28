"""
Alembic environment configuration with proper type checking.
"""

import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import engine_from_config
from alembic import context
from typing import Dict, Any, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.models import Base
from app.config import settings, get_database_url_safe

# Alembic Config object
config = context.config

# Get database URL safely
database_url = get_database_url_safe()
config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run async migrations for PostgreSQL."""
    connectable = create_async_engine(
        database_url,
        future=True,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_migration)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    db_url = database_url

    if "postgresql" in db_url:
        # Async mode for PostgreSQL
        asyncio.run(run_async_migrations())
    else:
        # Sync mode for SQLite with type-safe configuration
        section_config = config.get_section(config.config_ini_section)

        # Ensure configuration is not None
        if section_config is None:
            # Fallback to minimal configuration
            section_config = {}

        # Add database URL to configuration
        section_config['sqlalchemy.url'] = database_url

        connectable = engine_from_config(
            section_config,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata
            )

            with context.begin_transaction():
                context.run_migrations()


def do_migration(connection) -> None:
    """Synchronous function to run migrations."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
