from time import time
import random
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import logging


from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, __version__, HTTPException, Response, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.future import select

from schema import PenisDataResponse
from model import PenisData
from predictions_list import predictions
from db_manager import session_manager
from database import DBSessionDep


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    yield
    if session_manager.engine is not None:
        # Close the DB connection
        await session_manager.close()


app = FastAPI(lifespan=lifespan, debug=True)
app.add_middleware(
   CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials =True,
    allow_methods = ["*"],
    allow_headers= ["*"],
)



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
    async with db.begin():
        user = (await db.execute(select(PenisData).filter(PenisData.username == username))).scalar()

        if not user:
            user = PenisData(username=username, length=random.choice([-10, -5, 0, 5, 10]))
            db.add(user)
            return user  # This user will be committed and refreshed automatically at the end of the transaction block

        now = datetime.utcnow()
        if user.last_updated and (now - user.last_updated) < timedelta(hours=24):
            remaining_time = (now - user.last_updated)
            raise HTTPException(status_code=403, detail=f"You can only update points once every 24 hours. Please wait {remaining_time}.")

        change = random.choice([-10, -5, 0, 5, 10])
        user.length += change
        user.last_updated = now

    # User object will be automatically committed and refreshed here
    return user

@app.get("/points/{username}", response_model=PenisDataResponse)
async def get_points(username: str, db: DBSessionDep):
    try:
        user = (await db.execute(select(PenisData).filter(PenisData.username == username))).scalar()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        logging.error("Failed to get points: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    import traceback

    return Response(
        content="".join(
            traceback.format_exception(
                etype=type(exc), value=exc, tb=exc.__traceback__
            )
        )
    )
