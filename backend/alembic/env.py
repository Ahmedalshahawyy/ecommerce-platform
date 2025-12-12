from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool
import logging
import sys
import os

# allow importing backend package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend import db as db_module
from backend import models

config = context.config

# Use the application's SQLAlchemy URL
# Use the application's SQLAlchemy engine/URL if provided (supports env DATABASE_URL)
config.set_main_option('sqlalchemy.url', 'sqlite:///./ecommerce.db')

target_metadata = db_module.Base.metadata


    # prefer environment DATABASE_URL or the application's engine URL
    url = os.getenv('DATABASE_URL', str(getattr(db_module.engine, 'url', 'sqlite:///./ecommerce.db')))
    url = config.get_main_option('sqlalchemy.url')
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = db_module.engine

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
