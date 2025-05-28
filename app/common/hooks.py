import uuid

from flask import g
from flask import request
from flask import Response


def set_request_id():
    """
    获取单次请求的request_id
    """
    g.request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))


def inject_request_id(response: Response):
    """
    返回单次请求的request_id
    """
    response.headers["X-Request-Id"] = g.request_id
    return response


__all__ = ["set_request_id", "inject_request_id"]


