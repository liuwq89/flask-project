from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from conf.config import config
from app.common.log import ilog
from app.make_flask import make_flask
from app.make_celery import make_celery

# flask app init
flask_app = make_flask(__name__)

# Allow access to domains
CORS(flask_app, origins=flask_app.config["CORS_ALLOWED_ORIGINS"])

# sqlalchemy db init
db = SQLAlchemy(flask_app)
session = db.session
celery_db = db
celery_session = celery_db.session

# celery app init
celery_app = make_celery(flask_app)


# import app.common.flask_redis_connect
import app.auth.jwt_auth
import app.routes

