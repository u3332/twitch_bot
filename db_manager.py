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

        # Ensuring that the engine is always configured with the echo parameter
        # for debugging, which can be turned off by default or based on the environment.
        engine_kwargs.setdefault('echo', True)

        self.engine = create_async_engine(database_url, **engine_kwargs)
        self.SessionLocal = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            class_=AsyncSession
        )

    async def close(self):
        # Safeguard to check if the engine was already closed
        if self.engine is None:
            return
        await self.engine.dispose()
        self.engine = None
        self.SessionLocal = None

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        # Check if session maker exists
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
