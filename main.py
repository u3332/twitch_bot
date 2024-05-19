from time import time
import random
from datetime import datetime, timedelta
from contextlib import asynccontextmanager


from fastapi import FastAPI, __version__, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.future import select

from schema import PenisDataResponse
from model import PenisData
from predictions_list import predictions
from db_manager import sessionmanager
from database import DBSessionDep


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


app = FastAPI(lifespan=lifespan)


app.mount("/static", StaticFiles(directory="static"), name="static")

html = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>FastAPI on Vercel</title>
        <link rel="icon" href="/static/favicon.ico" type="image/x-icon" />
    </head>
    <body>
        <div class="bg-gray-200 p-4 rounded-lg shadow-lg">
            <h1>Hello from FastAPI@{__version__}</h1>
            <ul>
                <li><a href="/docs">/docs</a></li>
                <li><a href="/redoc">/redoc</a></li>
            </ul>
            <p>Powered by <a href="https://vercel.com" target="_blank">Vercel</a></p>
        </div>
    </body>
</html>
"""


@app.get("/")
async def root():
    return HTMLResponse(html)


@app.get('/ping')
async def hello():
    return {'res': 'pong', 'version': __version__, "time": time()}


@app.get('/prediction')
async def get_prediction():
    prediction = random.choice(predictions)
    return {'prediction': prediction}


@app.post("/update_points/{username}", response_model=PenisDataResponse)
async def update_points(username: str, db: DBSessionDep):
    result = await db.execute(select(PenisData).filter(PenisData.username == username))
    user = result.scalars().first()

    if not user:
        user = PenisData(username=username, length=random.choice([-10, -5, 0, 5, 10]))
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    now = datetime.utcnow()
    if user.last_updated and (now - user.last_updated) < timedelta(hours=24):
        remaining_time = timedelta(hours=24) - (now - user.last_updated)
        raise HTTPException(status_code=403,
                            detail=f"You can only update points once every 24 hours. Please wait {remaining_time}.")

    change = random.choice([-10, -5, 0, 5, 10])
    user.length += change
    user.last_updated = now

    await db.commit()
    await db.refresh(user)
    return user


@app.get("/points/{username}", response_model=PenisDataResponse)
async def get_points(username: str, db: DBSessionDep):
    result = await db.execute(select(PenisData).filter(PenisData.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
