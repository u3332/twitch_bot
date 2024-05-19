import contextlib
from typing import Any, AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from db_config import Config

Base = declarative_base()


class DatabaseSessionManager:
    def __init__(self, database_url: str, engine_kwargs: dict[str, Any] = None):
        if engine_kwargs is None:
            engine_kwargs = {}

        # Default engine configuration with debugging and pooling options
        engine_kwargs.setdefault('echo', True)  # For SQL debugging
        engine_kwargs.setdefault('pool_size', 10)  # The number of connections to keep open inside the connection pool
        engine_kwargs.setdefault('max_overflow', 10)  # The number of connections to allow in excess of `pool_size`
        engine_kwargs.setdefault('pool_timeout', 30)  # Seconds to wait before giving up on returning a connection
        engine_kwargs.setdefault('pool_recycle', -1)  # Reuse connections older than this number of seconds

        self.engine = create_async_engine(database_url, **engine_kwargs)
        self.SessionLocal = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            class_=AsyncSession
        )

    async def close(self):
        if self.engine is None:
            return
        await self.engine.dispose()
        self.engine = None
        self.SessionLocal = None

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self.SessionLocal is None:
            raise Exception("Session maker is not initialized")

        async_session = self.SessionLocal()
        try:
            yield async_session
            await async_session.commit()
        except Exception as e:
            await async_session.rollback()
            raise e
        finally:
            await async_session.close()


# Instance of the session manager
session_manager = DatabaseSessionManager(Config.SQLALCHEMY_DATABASE_URL)


async def get_db_session():
    async with session_manager.session() as session:
        yield session
