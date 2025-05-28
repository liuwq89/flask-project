import os
import logging.config

from flask import g

from conf.config import config


logging.config.fileConfig(os.path.join(config.ROOT_PATH, "conf/logging/logging.ini"))

ilog_root = logging.getLogger("ilog_root")
ilog_info = logging.getLogger("ilog_info")
ilog_warn = logging.getLogger("ilog_warn")
ilog_error = logging.getLogger("ilog_error")
ilog_access = logging.getLogger("ilog_access")


class RequestIDFilter(logging.Filter):
    """
    日志过滤器，动态从 flask.g 取 request_id 并注入日志记录。
    没有 request_id 时使用默认值 'no-request-id'
    """
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            record.request_id = getattr(g, "request_id", "no-request-id")
        except Exception:
            record.request_id = "no-request-id"
        return True


request_id_filter = RequestIDFilter()

ilog_info.addFilter(request_id_filter)
ilog_warn.addFilter(request_id_filter)
ilog_error.addFilter(request_id_filter)
ilog_access.addFilter(request_id_filter)


class ilog(object):
    info = ilog_info.info
    warn = ilog_warn.warning
    error = ilog_error.error
    access = ilog_access.info


__all__ = ["ilog"]



