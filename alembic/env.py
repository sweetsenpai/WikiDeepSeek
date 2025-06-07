import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import pool

from alembic import context

# Загружаем переменные окружения
load_dotenv()

# Эта строка должна быть ПОСЛЕ импорта context из alembic
config = context.config

# Настраиваем логгирование
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Устанавливаем URL базы данных из переменных окружения
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Импортируем ваши модели и metadata
from app.models import Base  # noqa

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
    from app.database import engine

    connectable = engine

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
