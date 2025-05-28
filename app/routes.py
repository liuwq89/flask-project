from flask_restful import Api

from app import flask_app
from app.uri.heartbeat import heartbeat_uri

api = Api(flask_app)

# heartbeat
heartbeat_uri.register(api)




