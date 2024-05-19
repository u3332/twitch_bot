import os
from dotenv import load_dotenv
load_dotenv('.env.development.local')


class Config:
    POSTGRES_USER = os.environ.get('POSTGRES_USER')
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    POSTGRES_DATABASE = os.environ.get('POSTGRES_DATABASE')
    SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DATABASE}"
