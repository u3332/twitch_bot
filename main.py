import logging
from time import time
import random
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from urllib.parse import unquote
from unidecode import unidecode

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, __version__, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from model import PenisData
from predictions_list import predictions, user_prediction
from db_manager import session_manager
from database import DBSessionDep
from user_cache import UserCache


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


user_cache = UserCache()
app = FastAPI(lifespan=lifespan, debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "version": __version__,
        "current_year": datetime.now().year
    })


@app.get('/ping')
async def hello():
    return {'res': 'pong', 'version': __version__, "time": time()}


@app.get("/prediction", response_model=str)
async def get_prediction(user: str, touser: str):
    logger.info('Raw user: %s', user)
    logger.info('Raw touser: %s', touser)

    # Process user and touser to be ASCII only
    caller = unidecode(user).strip()
    callee = unidecode(unquote(touser)).strip()

    logger.info('Processed caller: %s', caller)
    logger.info('Processed callee: %s', callee)

    # Validate callee with ASCII check
    if (not callee or
        not callee.isprintable() or
        callee.lower() == 'null' or
        callee.isspace() or
        not all(ord(char) < 128 for char in callee)):
        logger.info('Invalid callee detected (non-ASCII or empty), setting callee to caller')
        callee = caller

    logger.info('Final caller: %s', caller)
    logger.info('Final callee: %s', callee)

    if caller == callee:
        # Same person is calling
        prediction = random.choice(predictions)
        logger.info('Prediction for same caller and callee: %s', prediction)
    else:
        # Different person is calling
        prediction = random.choice(user_prediction).format(username=callee)
        logger.info('Prediction for different caller and callee: %s', prediction)

    return prediction


@app.get("/update_length/{username}", response_model=str)
def update_length(username: str, db: DBSessionDep):
    try:
        cached_response = user_cache.get(username)
        if cached_response:
            return cached_response

        user = db.execute(select(PenisData).filter(PenisData.username == username)).scalar()
        penis_prefix = random.choice(
            ['піструн', 'шланг', 'член', 'удав', 'прутень', 'вялий', 'стержень', 'стрижень', 'ствол', 'блохастий',
             'волохатий', 'лисий'])

        now = datetime.utcnow()
        if not user:
            new_length = random.randint(-10, 10)
            user = PenisData(username=username, length=new_length, last_updated=now)
            db.add(user)
            db.commit()
            db.refresh(user)
            response = f"{username}, у тебе з'явився {penis_prefix}, і його довжина: {new_length} см."
            user_cache.update_top5(user.username, new_length)
            return response

        if (username not in ['onenBoy', 'ruslanyeremichuk']
                and user.last_updated
                and (now - user.last_updated) < timedelta(hours=10)):
            response = f"Лінійка зламалася, перевіриш завтра! Наразі в тебе: {user.length} см"
            user_cache.set(username, user.length, response, last_updated=user.last_updated)
            return response

        change = random.randint(-10, 10)
        user.length += change
        user.last_updated = now
        db.commit()
        db.refresh(user)

        if change >= 0:
            response = f"{username}, я тебе вітаю! Твій {penis_prefix} виріс на {abs(change)} см. Поточна довжина: {user.length} см."
        elif change == 0:
            response = f"{username}, вважай, що тобі почастило. Твій {penis_prefix} не змінився в розмірі. Поточна довжина: {user.length} см."
        else:
            response = f"{username}, їбать ти лох! Твій {penis_prefix} зменшився на {abs(change)} см. Поточна довжина: {user.length} см."

        user_cache.set(username, user.length, response, last_updated=now)
        return response

    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Database error: {str(e)}", exc_info=True)
        return "Помилка бази даних, вибачай!"
    except Exception as e:
        db.rollback()
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        return "Неочікувана помилка, вибачай!"


@app.get("/top5", response_model=str)
async def get_top5():
    """
    Endpoint to retrieve the top 5 users based on length.
    Returns a formatted string with each username and their length.
    """
    if not user_cache.top5:
        return "No top users available."

    # Format the list into a single string
    result = "ТОП 5 ХУЯК: " + "; ".join(f"{user['username']} - {user['length']} см" for user in user_cache.top5)
    return result
