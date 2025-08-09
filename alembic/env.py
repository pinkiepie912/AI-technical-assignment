import os
import sys
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

# Load environment variables from .env file
load_dotenv(".env-migrations")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your project's root to sys.path to allow imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# Import the Base from your model definition

from db.model import Base

# Dynamically discover all models
project_root = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

for p in src_path.glob("**/orm/*.py"):
    if p.name != "__init__.py":
        module_name = (
            p.relative_to(src_path).with_suffix("").as_posix().replace("/", ".")
        )
        try:
            __import__(module_name)
        except ImportError as e:
            print(f"Could not import {module_name}: {e}")


target_metadata = Base.metadata


def get_db_url() -> str:
    engine = os.getenv("DB_WRITE_ENGINE")
    port = os.getenv("DB_WRITE_PORT")
    url = os.getenv("DB_WRITE_URL")
    db_name = os.getenv("DB_WRITE_NAME")
    user = os.getenv("DB_WRITE_USER")
    password = os.getenv("DB_WRITE_PASSWORD")
    return f"{engine}://{user}:{password}@{url}:{port}/{db_name}"


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_db_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        {"sqlalchemy.url": get_db_url()},
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
