import os

from urllib.parse import quote
from celery.schedules import crontab

from place_holder import __file__ as place_holder_file


# setting app root path
ROOT_PATH = os.path.dirname(os.path.abspath(place_holder_file))

