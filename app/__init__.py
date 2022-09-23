from flask import Flask
from config import Development, DockerConfig, TestConfig
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

#Set app's config
app.config.from_object(DockerConfig)

#Instantiate Celery
celery = Celery(
    __name__, broker=app.config['BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'], result_expires=300
)

#Instantiate DB
db = SQLAlchemy(app)

#Instantiate Migration
migrate = Migrate(app, db, compare_type=True)

from app import routes, models
