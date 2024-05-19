import logging
from time import time
import random
from datetime import datetime, timedelta
from contextlib import asynccontextmanager


from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, __version__
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

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
        session_manager.close()


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


@app.post("/update_length/{username}", response_model=str)
def update_length(username: str, db: DBSessionDep):
    try:
        user = db.execute(select(PenisData).filter(PenisData.username == username)).scalar()
        penis_prefix = random.choice(['піструн', 'шланг', 'член', 'удав', 'прутень', 'вялий', 'стержень', 'стрижень', 'ствол', 'блохастий', 'волохатий', 'лисий'])


        if not user:
            new_length = random.randint(-10, 10)
            user = PenisData(username=username, length=new_length)
            db.add(user)
            db.commit()
            db.refresh(user)
            return f"{username}, у тебе з'явився {penis_prefix}, і його довжина - {new_length} см."

        now = datetime.utcnow()
        if user.last_updated and (now - user.last_updated) < timedelta(hours=10):
            return f"Лінійка зламалася, перевіриш завтра! Наразі в тебе: {user.length} см"

        change = random.randint(-10, 10)
        user.length += change
        user.last_updated = now
        db.commit()
        db.refresh(user)
        if change >= 0:
            return f"{username}, я тебе вітаю! Твій {penis_prefix} виріс на {abs(change)} см. Поточна довжина: {user.length} см."
        elif change == 0:
            return f"{username}, вважай, що тобі почастило. Твій {penis_prefix} не змінився в розмірі. Поточна довжина: {user.length} см."
        else:
            return f"{username}, їбать ти лох! Твій {penis_prefix} зменшився на {abs(change)} см. Поточна довжина: {user.length} см."
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Database error: {str(e)}", exc_info=True)
        return "Помилка бази даних, вибачай!"
    except Exception as e:
        db.rollback()
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        return "Неочікувана помилка, вибачай!"
