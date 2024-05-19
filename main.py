from time import time
from fastapi import FastAPI, __version__
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import random

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
    '''Сьогодні ти лузонеш три гри''',
    '''Бро, ти нарвешся на луз стрік''',
    '''Якщо підеш в соло, то програєш''',
    '''Якщо не підпишешся на мій ТГ, то тебе зловить ТЦК''',
    '''Сьогодні в тебе буде с3кс, але тобі обирати з ким''',
    '''Ти отримаєш гарну звістку''',
    '''Відкривай кейс, відчуваю що там ніж''',
    '''Ти вип'єш склянку води''',
    '''В тебе під вікнами стоїть чорний бусік, будь обережний''',
    '''В тебе у житті розпочнеться біла полоса, тому не бійся і скидай мені 200 грн на карту''',
    '''Я відчуваю, що тобі треба скинути пар, тому не бійся і зроби це ( ͡° ͜ʖ ͡°)'''
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
