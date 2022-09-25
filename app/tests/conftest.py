import pytest, os
from app import app, models
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker': 'redis://localhost:6379/0',
        'result': 'redis://localhost:6379/0',
    }