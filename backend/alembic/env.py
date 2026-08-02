from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import os
import sys
from dotenv import load_dotenv

# Προσθέτει τον φάκελο backend/ στο "path" της Python, ώστε να μπορούμε
# να κάνουμε import το δικό μας πακέτο "app" από εδώ μέσα
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Φορτώνει το .env, ώστε να έχουμε πρόσβαση στο DATABASE_URL
load_dotenv()

# Εισάγουμε το Base και το Country model, ώστε το Alembic να τα "βλέπει"
from app.core.database import Base
from app.models.country import Country
from app.models.indicator import Indicator
from app.models.negotiation_event import NegotiationEvent, EventParticipant
from app.models.user import User
from app.models.negotiation_analysis import NegotiationAnalysis

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Εδώ λέμε στο Alembic ποια models να παρακολουθεί
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    # Παίρνουμε το connection string από το .env αντί από το alembic.ini
    database_url = os.getenv("DATABASE_URL")
    config.set_main_option("sqlalchemy.url", database_url)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()