# migrations/env.py — FINAL WORKING VERSION
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your app and models
from app import db
from app.models.user import User
from app.models.goal import Goal
from app.models.task import Task

# Use db.metadata directly
target_metadata = db.metadata

# Load alembic.ini
fileConfig(context.config.config_file_name)

def run_migrations_offline():
    url = context.config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    # Get URL from Flask config via environment variable
    from app.config import Config
    connectable = engine_from_config(
        {"sqlalchemy.url": Config.SQLALCHEMY_DATABASE_URI},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()