from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from contextlib import asynccontextmanager
import logging

from backend.db_models.base import Base
from backend.core.config import settings

# Configurazione logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(
    logging.INFO if settings.DB_ECHO else logging.WARNING
)


# Configurazione dell'engine asincrono
async_engine = create_async_engine(
    settings.ASYNC_SQLITE_DB_PATH,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=settings.DB_ECHO
)

# Session factory asincrona
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

@asynccontextmanager
async def get_db_session() -> AsyncSession:
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

async def get_db() -> AsyncSession:
    async with get_db_session() as session:
        yield session


async def check_index_exists(conn, table_name, index_name):
    """Verifica asincrona se un indice esiste"""
    result = await conn.execute(
        text(
            f"SELECT name FROM sqlite_master "
            f"WHERE type='index' AND name='{index_name}' "
            f"AND tbl_name='{table_name}'"
        )
    )
    return result.scalar() is not None


async def async_init_db():
    """Inizializzazione completa del database in modalità asincrona"""
    try:
        async with async_engine.begin() as conn:
            # Crea tutte le tabelle
            await conn.run_sync(Base.metadata.create_all)

            # Verifica e crea indici mancanti
            inspector = await conn.run_sync(lambda sync_conn: inspect(sync_conn))
            existing_tables = await conn.run_sync(
                lambda sync_conn: inspector.get_table_names()
            )

            if 'users' in existing_tables:
                if not await check_index_exists(conn, 'users', 'ix_users_email'):
                    await conn.execute(
                        text("CREATE UNIQUE INDEX ix_users_email ON users (email)")
                    )
                    logging.info("Created index ix_users_email on users table")

            if 'workout_assignments' in existing_tables:
                if not await check_index_exists(conn, 'workout_assignments', 'ix_wa_user_workout'):
                    await conn.execute(
                        text("CREATE INDEX ix_wa_user_workout ON workout_assignments (user_id, workout_id)")
                    )
                    logging.info("Created index ix_wa_user_workout on workout_assignments table")

    except Exception as e:
        logging.error(f"Database initialization failed: {str(e)}")
        raise


async def async_reset_db():
    """Resetta completamente il database (solo per sviluppo)"""
    if not settings.DEV_MODE:
        raise RuntimeError("Database reset is only allowed in development mode")

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        logging.info("Database reset completed")




# Verifica automatica all'avvio in modalità sviluppo
if __name__ == "__main__":
    import asyncio

    asyncio.run(async_init_db())

