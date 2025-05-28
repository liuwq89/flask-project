from flask import Flask
from celery import Celery

from app import celery_config


def make_celery(flask_app: Flask) -> Celery:
    """
    初始化 Celery app 实例
    """
    celery_app = Celery(flask_app.name)
    celery_app.config_from_object(celery_config)
    celery_app.autodiscover_tasks(celery_config.CELERY_IMPORTS)

    class ContextTask(celery_app.Task):
        """
        celery 自动注入 flask 上下文
        让所有任务继承 ContextTask
        """
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)
        
    celery_app.Task = ContextTask
    return celery_app


