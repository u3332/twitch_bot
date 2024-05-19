from time import time
import random
from datetime import datetime, timedelta

from fastapi import FastAPI, __version__, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from schema import PenisDataResponse
from session import create_get_session
from model import PenisData

app = FastAPI()
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

predictions = [
    '''Стартуй каточку прямо зараз, ізі він для тебе''',
    '''Сьогодні ти лузонеш три гри''',
    '''Бро будь обрежнішим, бо ти нарвешся на луз стрік''',
    '''Якщо підеш в соло, то програєш''',
    '''Якщо не підпишешся на мій ТГ, то тебе зловить ТЦК''',
    '''Сьогодні в тебе буде с3кс, але тобі обирати з ким''',
    '''Ти отримаєш гарну звістку''',
    '''Відкривай кейс, відчуваю що там ніж''',
    '''Випий скляночку водички!''',
    '''В тебе під вікнами стоїть чорний бусік, будь обережний''',
    '''В тебе у житті розпочнеться біла полоса, тому не бійся і скидай мені 200 грн на карту''',
    '''Я відчуваю, що тобі треба скинути пар, тому не бійся і зроби це ( ͡° ͜ʖ ͡°)''',
    '''Час покормити свого удава ٩(˘◡˘)۶''',
    '''Чекаю твою фоточку в себе в ЛС''',
    '''Самий час вийти на прогулянку, щоб понюхати беброчку''',
    '''Якщо здається, що в тебе''',
    '''Мий ножки та лягай спатки, я дострімлю і ляжу поруч із тобою, бро :)''',
    '''Не важливо який в тебе розмір, важливо як ти ним користуєшся ʕ•́ᴥ•̀ʔっ''',
    '''Ти можеш скільки хочеш брехати оточуючим, але собі брехати не варто. Подумай над цим!''',
    '''Я бачу, що ти підкований в сексуальній теорії, тому пора приступати до практики''',
    '''Важливо слухати свою душу і робити так як хочеш саме ти <33''',
    '''Ти пам'ятаєш про що обіцяєш собі перед сном?''',
    '''Зроби зараз 10 присідань, щоб накачати свій горішок і всі дівчата були твої''',
    '''Мріяти не достатньо, тому раджу почати діяти (говорю як успішна людина).''',
    '''Якщо ти перейдеш до мене в телеграм !тг - матимеш можливість отримати...''',
    '''Гарний стрім, офай'''
]


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
def update_points(username: str, db: Session = Depends(create_get_session)):
    user = db.query(PenisData).filter(PenisData.username == username).first()

    if not user:
        user = PenisData(username=username, length=random.choice([-10, -5, 0, 5, 10]))
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    now = datetime.utcnow()
    if user.last_updated and (now - user.last_updated) < timedelta(hours=24):
        remaining_time = timedelta(hours=24) - (now - user.last_updated)
        raise HTTPException(status_code=403,
                            detail=f"You can only update points once every 24 hours. Please wait {remaining_time}.")

    change = random.choice([-10, -5, 0, 5, 10])
    user.length += change
    user.last_updated = now

    db.commit()
    db.refresh(user)
    return user


@app.get("/points/{username}", response_model=PenisDataResponse)
def get_points(username: str, db: Session = Depends(create_get_session)):
    user = db.query(PenisData).filter(PenisData.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
