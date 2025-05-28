import traceback
from functools import wraps

from flask import request
from flask import Response
from werkzeug import exceptions
from flask_jwt_extended import jwt_required

from app import db, session
from app.common.log import ilog
from app.common.common_func import http_resp
from app.common.constants import FAILED_CODE


def method_control(func):
    """
    请求方法控制器
    """
    @wraps(func)
    def wrapper(obj, *args, **kwargs):
        if func.__name__.upper() in list(obj.ALLOW_METHOD.keys()):
        # if request.method.upper() in list(obj.ALLOW_METHOD.keys()):
            return func(obj, *args, **kwargs)
        else:
            return http_resp(
                code=FAILED_CODE,
                message='%s method is not allowed' % func.__name__.upper(),
                request_id=obj.request_id,
                status=404,
            )
    return wrapper


def has_permission(func):
    """
    权限验证
    """
    @wraps(func)
    def wrapper(obj, *args, **kwargs):
        # TODO (权限验证)
        return func(obj, *args, **kwargs)
    return wrapper


def retult_cache(func):
    """
    缓存
    """
    @wraps(func)
    def wrapper(obj, *args, **kwargs):
        # TODO (缓存)
        return func(obj, *args, **kwargs)
    return wrapper


def access_logger(func):
    """
    请求记录
    """
    @wraps(func)
    def wrapper(obj, *args, **kwargs):
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        url = request.path
        method = request.method.upper()
        params = _get_all_params()
        try:
            ret: Response = func(obj, *args, **kwargs)
        except exceptions.BadRequest as e:
            raise e
        except Exception as e:
            ret = http_resp(FAILED_CODE, "服务出错", request_id=obj.request_id, status=500)
            ilog.error("request error: ip=%s, method=%s, url=%s, status=%s, params=%s, err_msg=%s" % (
                ip, method, url, ret.status_code, params, traceback.format_exc()
            ))
        finally:
            if hasattr(obj, "model") and obj.model and method != "GET":
                db.session.rollback()
        # Case1: log save.
        ilog.access("access: ip=%s, method=%s, url=%s, status=%s, params=%s" % (
            ip, method, url, ret.status_code, params
        ))
        return ret
        # Case2: db save.
        # log = AccessLogModel()
        # db.session.add(log)
        # db.session.commit()
    return wrapper


def _get_all_params():
    """
    获取 args / form / json 所有参数
    """
    params = {}
    params.update(request.values.to_dict())
    params.update(request.get_json(silent=True) or {})
    return params


__all__ = ["method_control", "jwt_required", "has_permission", "retult_cache", "access_logger"]

