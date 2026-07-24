from logging.config import fileConfig
from pathlib import Path
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context


# Adiciona a raiz do projeto ao caminho de importação do Python.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.core.config import settings
from app.database.base import Base
from app.models import Team
from ultrastats_ai.infrastructure.database.models import CanonicalBase


# Objeto de configuração do Alembic.
config = context.config


# Configura o sistema de logs usando o alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Informa ao Alembic quais modelos devem ser analisados.
target_metadata = [Base.metadata, CanonicalBase.metadata]


def run_migrations_offline() -> None:
    """
    Executa as migrações sem abrir uma conexão direta
    com o banco de dados.
    """

    url = settings.database_url

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Executa as migrações conectando diretamente
    ao PostgreSQL.
    """

    configuration = config.get_section(
        config.config_ini_section
    ) or {}

    configuration["sqlalchemy.url"] = settings.database_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
