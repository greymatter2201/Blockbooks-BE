from flask import Flask
from config import Config
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from celery import Celery
from flask_cors import CORS
from flask_migrate import Migrate

#Instantiate Flask
app = Flask(__name__)

#Instantiate CORS
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=[
    "Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
    supports_credentials=True, intercept_exceptions=False)

#Instantiate API
api = Api(app)

#Instantiate Sockets // Currently not in used
socketio = SocketIO(app)

#Instantiate Celery
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
celery = Celery(__name__, broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

#Set app's config
app.config.from_object(Config)

#Instantiate DB
db = SQLAlchemy(app)

#Instantiate Migration
migrate = Migrate(app, db)

from app import routes
