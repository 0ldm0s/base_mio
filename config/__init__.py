# -*- coding: utf-8 -*-
import os
from urllib.parse import quote_plus

basedir = os.path.abspath(os.path.dirname(__file__))
MIO_HOST = os.environ.get("MIO_HOST", "127.0.0.1")
MIO_PORT = int(os.environ.get("MIO_PORT", 5050))
MIO_SITE_HOST = os.environ.get("MIO_SITE_HOST", MIO_HOST)
MIO_GQL_ADMIN_KEY = "gql:api:admin"
# 这个默认为当前最新版本，旧版就不在这里定义了
MIO_GQL_USER_API_KEY = "gql:api:user"
REDIS_PASSWORD_HASH_KEY = "PlatformUser:PasswordHash:{}"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "PNo3leuTFG84Z$1hPWooO1GG4jELL3O1"  # 默认秘钥
    SESSION_TYPE = "filesystem"
    # 邮件系统设置相关
    MIO_MAIL = False
    MIO_SEND_MAIL = False
    MAIL_SUBJECT_PREFIX = os.environ.get("MIO_MAIL_SUBJECT_PREFIX", "[Mio System]")  # 默认邮件标题前缀
    MAIL_DEFAULT_SENDER = \
        os.environ.get("MIO_MAIL_DEFAULT_SENDER", "Mio System Administrator <admin@example.com>")  # 默认发件人
    MAIL_SERVER = os.environ.get("MIO_MAIL_SERVER", "localhost")
    MAIL_PORT = os.environ.get("MIO_MAIL_PORT", 25)
    MAIL_USE_TLS = os.environ.get("MIO_MAIL_USE_TLS", False)
    MAIL_USE_SSL = os.environ.get("MIO_MAIL_USE_SSL", False)
    MAIL_USERNAME = os.environ.get("MIO_MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MIO_MAIL_PASSWORD", "")
    # 是否使用MONGODB
    MONGODB_ENABLE = os.environ.get("MIO_MONGODB_ENABLE", False)
    # 是否使用关系型数据库
    RDBMS_ENABLE = os.environ.get("MIO_RDBMS_ENABLE", False)
    # 是否使用CELERY
    CELERY_ENABLE = os.environ.get("MIO_CELERY_ENABLE", False)
    # 是否使用Redis
    REDIS_ENABLE = os.environ.get("MIO_REDIS_ENABLE", False)
    # Redis前导
    REDIS_KEY_PREFIX = "PYMIO"
    # 是否使用CACHE
    CACHED_ENABLE = os.environ.get("MIO_CACHED_ENABLE", False)
    # 是否使用CORS
    CORS_ENABLE = os.environ.get("MIO_CORS_ENABLE", False)
    CORS_URI = os.environ.get("MIO_CORS_URI", {r"/*": {"origins": "*"}})
    # 支持的语言
    LANGUAGES = ["zh-CN"]
    # 默认语言
    DEFAULT_LANGUAGE = "zh-CN"
    # 默认时区
    MIO_TIMEZONE = "Asia/Shanghai"

    @staticmethod
    def init_app(app):
        app.jinja_env.trim_blocks = True
        app.jinja_env.lstrip_blocks = True


class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_USER = "admin"
    MONGODB_PASSWORD = "password"
    MONGODB_HOST = "localhost"
    MONGODB_DB = "dbname"
    MONGODB_SETTINGS = {
        "host": "mongodb://{user}:{password}@{host}/{db}?directConnection=true&compressors=zstd".format(
            user=quote_plus(MONGODB_USER), password=quote_plus(MONGODB_PASSWORD), host=MONGODB_HOST, db=MONGODB_DB),
        "connect": False
    }
    SQLALCHEMY_DATABASE_USER = "admin"
    SQLALCHEMY_DATABASE_PASSWORD = "password"
    SQLALCHEMY_DATABASE_HOST = "localhost:5432"
    SQLALCHEMY_DATABASE_DB = "dbname"
    SQLALCHEMY_DATABASE_URI = "postgresql+pg8000://{user}:{password}@{host}/{db}".format(
        user=quote_plus(SQLALCHEMY_DATABASE_USER), password=quote_plus(SQLALCHEMY_DATABASE_PASSWORD),
        host=SQLALCHEMY_DATABASE_HOST, db=SQLALCHEMY_DATABASE_DB)
    REDIS_URL = "redis://localhost:6379/0"
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = REDIS_URL
    CELERY_BROKER_URL = REDIS_URL
    CELERY_BACKEND_URL = REDIS_URL


class TestingConfig(Config):
    TESTING = True
    MONGODB_USER = "admin"
    MONGODB_PASSWORD = "password"
    MONGODB_HOST = "localhost"
    MONGODB_DB = "dbname"
    MONGODB_SETTINGS = {
        "host": "mongodb://{user}:{password}@{host}/{db}?directConnection=true&compressors=zstd".format(
            user=quote_plus(MONGODB_USER), password=quote_plus(MONGODB_PASSWORD), host=MONGODB_HOST, db=MONGODB_DB),
        "connect": False
    }
    SQLALCHEMY_DATABASE_USER = "admin"
    SQLALCHEMY_DATABASE_PASSWORD = "password"
    SQLALCHEMY_DATABASE_HOST = "localhost:5432"
    SQLALCHEMY_DATABASE_DB = "dbname"
    SQLALCHEMY_DATABASE_URI = "postgresql+pg8000://{user}:{password}@{host}/{db}".format(
        user=quote_plus(SQLALCHEMY_DATABASE_USER), password=quote_plus(SQLALCHEMY_DATABASE_PASSWORD),
        host=SQLALCHEMY_DATABASE_HOST, db=SQLALCHEMY_DATABASE_DB)
    REDIS_URL = "redis://localhost:6379/0"
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = REDIS_URL
    CELERY_BROKER_URL = REDIS_URL
    CELERY_BACKEND_URL = REDIS_URL


class ProductionConfig(Config):
    MONGODB_USER = "admin"
    MONGODB_PASSWORD = "password"
    MONGODB_HOST = "localhost"
    MONGODB_DB = "dbname"
    MONGODB_SETTINGS = {
        "host": "mongodb://{user}:{password}@{host}/{db}?directConnection=true&compressors=zstd".format(
            user=quote_plus(MONGODB_USER), password=quote_plus(MONGODB_PASSWORD), host=MONGODB_HOST, db=MONGODB_DB),
        "connect": False
    }
    SQLALCHEMY_DATABASE_USER = "admin"
    SQLALCHEMY_DATABASE_PASSWORD = "password"
    SQLALCHEMY_DATABASE_HOST = "localhost:5432"
    SQLALCHEMY_DATABASE_DB = "dbname"
    SQLALCHEMY_DATABASE_URI = "postgresql+pg8000://{user}:{password}@{host}/{db}".format(
        user=quote_plus(SQLALCHEMY_DATABASE_USER), password=quote_plus(SQLALCHEMY_DATABASE_PASSWORD),
        host=SQLALCHEMY_DATABASE_HOST, db=SQLALCHEMY_DATABASE_DB)
    REDIS_URL = "unix:///dev/shm/redis.sock?db=0"
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = REDIS_URL
    CELERY_BROKER_URL = "redis://localhost:6379/1"
    CELERY_BACKEND_URL = CELERY_BROKER_URL


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,

    "default": DevelopmentConfig
}
