from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool


from alembic import context

from app import models

# Set the target_metadata variable to the metadata object associated with your database schema
target_metadata = models.Base.metadata

# this is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    # When using the context manager with connectable, the connection and transaction are
    # managed automatically. When the context manager exits, the transaction is committed.
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


# If alembic is run offline (without database connection)
# The function run_migrations_offline will be called
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
