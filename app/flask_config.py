# flask app config

from conf.config import config


# timezone
TIMEZONE = config.TIMEZONE

# app debug
DEBUG = config.DEBUG

# app host
HOST = config.APP_HOST

# app port
PORT = config.APP_PORT

# allow access to domains
CORS_ALLOWED_ORIGINS = config.CORS_ALLOWED_ORIGINS

# jwt config
JWT_SECRET_KEY = 'Your Secret Key'
JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 2

# sqlalchemy config
# 连接池中连接的最大重用时间
SQLALCHEMY_POOL_RECYCLE = config.SQLALCHEMY_POOL_RECYCLE
# 禁用对象修改追踪功能
SQLALCHEMY_TRACK_MODIFICATIONS = config.SQLALCHEMY_TRACK_MODIFICATIONS
# default db uri
SQLALCHEMY_DATABASE_URI = config.SQLALCHEMY_DATABASE_URI
# other dbs uri (take effect by '__bind_key__')
SQLALCHEMY_BINDS = config.SQLALCHEMY_BINDS


