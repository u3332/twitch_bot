import contextlib
from typing import Any, Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from db_config import Config

Base = declarative_base()


class DatabaseSessionManager:
    def __init__(self, database_url: str, engine_kwargs: dict[str, Any] = None):
        if engine_kwargs is None:
            engine_kwargs = {}

        engine_kwargs.setdefault('echo', True)
        engine_kwargs.setdefault('pool_size', 10)
        engine_kwargs.setdefault('max_overflow', 10)
        engine_kwargs.setdefault('pool_timeout', 30)
        engine_kwargs.setdefault('pool_recycle', 1800)  # Consider a positive recycle time

        self.engine = create_engine(database_url, **engine_kwargs)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def close(self):
        if self.engine is None:
            return
        self.engine.dispose()
        self.engine = None
        self.SessionLocal = None

    @contextlib.contextmanager
    def session(self) -> Iterator[Session]:
        if self.SessionLocal is None:
            raise Exception("Session maker is not initialized")

        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


# Instance of the session manager
session_manager = DatabaseSessionManager(Config.SQLALCHEMY_DATABASE_URL)


def get_db_session():
    with session_manager.session() as session:
        yield session
