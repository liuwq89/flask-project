# celery app config

from conf.config import config


# celery stop utc time and timezone is efficient
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = config.TIMEZONE

# celery broker conf
CELERY_BROKER_URL = config.CELERY_BROKER_URL

# celery result conf
CELERY_RESULT_BACKEND = config.CELERY_RESULT_BACKEND

# celery discover task
CELERY_IMPORTS = ["app.tasks"]

# celery schedule config
# CELERY_BEAT_SCHEDULE = {
    # "celery_task_every_five_min": {
    #     "task": "app.tasks.upload.xxxxx",
    #     "schedule": crontab(minute="*/5"),
    #     "options": {"queue": "task_queue"},
    # },
    # 'celery_task_every_wednesday_10h': {
    #     'task': 'app.tasks.upload.xxxxx',
    #     'schedule': crontab(hour=10, minute=0, day_of_week=3),
    # },
# }


