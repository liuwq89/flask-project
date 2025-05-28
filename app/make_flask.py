from flask import Flask

from app import flask_config
from app.common.hooks import *


def make_flask(import_name: str) -> Flask:
    """
    初始化 Flask app 实例
    """
    flask_app = Flask(import_name)
    flask_app.config.from_object(flask_config)

    # add request hooks
    flask_app.before_request(set_request_id)
    flask_app.after_request(inject_request_id)

    return flask_app



