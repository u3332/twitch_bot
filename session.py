import model
from database import SessionLocal, engine


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(model.Base.metadata.create_all)


async def create_get_session():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
