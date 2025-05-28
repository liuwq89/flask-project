from conf.config.base import *
from conf.config.load_global_conf import global_conf


# app config
DEBUG = True
APP_HOST = "0.0.0.0"
APP_PORT = 9898
CORS_ALLOWED_ORIGINS = "*"
TIMEZONE = "Asia/Shanghai"

# mysql config
# default db
MYSQL_HOST = global_conf.get("mysql_host")
MYSQL_PORT = int(global_conf.get("mysql_port", 23306))
MYSQL_USER = global_conf.get("mysql_user")
MYSQL_PASSWORD = quote(global_conf.get("mysql_password", ""))
MYSQL_DB_NAME = global_conf.get("mysql_db_name", "flask_default_db")

# other dbs
MYSQL_OTHER_HOST = global_conf.get("mysql_other_host")
MYSQL_OTHER_PORT = int(global_conf.get("mysql_other_port", 23306))
MYSQL_OTHER_USER = global_conf.get("mysql_other_user")
MYSQL_OTHER_PASSWORD = quote(global_conf.get("mysql_other_password", ""))
MYSQL_OTHER_DB_NAME = global_conf.get("mysql_other_db_name", "flask_other_db")

# sqlachemy config
SQLALCHEMY_POOL_RECYCLE = 60 * 30
SQLALCHEMY_TRACK_MODIFICATIONS = False

# default db config of sqlachemy
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://%s:%s@%s:%s/%s" % \
        (MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DB_NAME)

# other dbs config of sqlachemy
SQLALCHEMY_BINDS = {
    "other_db": "mysql+pymysql://%s:%s@%s:%s/%s" % 
        (MYSQL_OTHER_USER, MYSQL_OTHER_PASSWORD, MYSQL_OTHER_HOST, MYSQL_OTHER_PORT, MYSQL_OTHER_DB_NAME),
}

# redis config
REDIS_CONFIG = {
    "PUBLIC": {
        "HOST": global_conf.get("redis_public_host"),
        "PORT": int(global_conf.get("redis_public_port")),
        "PASSWORD": global_conf.get("redis_public_password"),
        "DB": int(global_conf.get("redis_public_db", 0)),
    },
    "CELERY": {
        "HOST": global_conf.get("celery_broker_host"),
        "PORT": global_conf.get("celery_broker_port"),
        "PASSWORD": global_conf.get("celery_broker_password"),
        "DB": int(global_conf.get("celery_broker_db", 1))
    }
}

# celery config
CELERY_BROKER_URL = "redis://:%s@%s:%s/%s" % (
    REDIS_CONFIG["CELERY"]["PASSWORD"], REDIS_CONFIG["CELERY"]["HOST"],
    REDIS_CONFIG["CELERY"]["PORT"], REDIS_CONFIG["CELERY"]["DB"]
)
CELERY_RESULT_BACKEND = CELERY_BROKER_URL



