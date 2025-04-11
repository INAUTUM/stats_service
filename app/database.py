from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Асинхронный движок для FastAPI
ASYNC_DB_URL = "postgresql+asyncpg://postgres:example@db:5432/postgres"
engine = create_async_engine(ASYNC_DB_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Синхронный движок для Celery
SYNC_DB_URL = "postgresql://postgres:example@db:5432/postgres"
sync_engine = create_engine(SYNC_DB_URL)
SyncSessionLocal = sessionmaker(sync_engine)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Асинхронный движок
engine = create_async_engine(
    ASYNC_DB_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)

# Синхронный движок
sync_engine = create_engine(
    SYNC_DB_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)