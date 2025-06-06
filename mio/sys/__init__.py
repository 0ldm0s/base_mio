# -*- coding: UTF-8 -*-
import os
import re
import sys
import rtoml as tomllib
import time
import codecs
import logging
import asyncio
import importlib
from pathlib import Path
from celery import Celery
from flask import Flask, blueprints
from flask_cors import CORS
from flask_babel import Babel
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_redis import FlaskRedis
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from typing import Tuple, Optional, List, Union
from mio.util.Helper import in_dict, is_enable, is_number, get_canonical_os_name, get_args_from_dict
from mio.util.Logs import LogHandler, LoggerType, nameToLevel
from mio.sys.json import MioJsonProvider
from mio.sys.flask_mongoengine import MongoEngine

MIO_SYSTEM_VERSION = "2.0.2"
mail = None
crypt: Bcrypt = Bcrypt()
db: Optional[MongoEngine] = None
rdb: Optional[SQLAlchemy] = None
redis_db: Optional[FlaskRedis] = None
csrf: Optional[CSRFProtect] = None
cache: Optional[Cache] = None
babel: Optional[Babel] = None
celery_app: Optional[Celery] = None
os_name: str = get_canonical_os_name()


def create_app(
        config_name: str, root_path: Optional[str] = None, config_clz: Optional[str] = None,
        is_cli: bool = False, logger_type: LoggerType = LoggerType, log_level: int = logging.DEBUG
) -> Tuple[Flask, LogHandler]:
    global cache, babel, csrf, redis_db, db, rdb, mail, celery_app
    console = LogHandler("PyMio", logger_type=logger_type, log_level=log_level)
    console.info(f"Initializing the system......profile: {config_name}")
    console.info(f"Pymio Version: {MIO_SYSTEM_VERSION}")
    config_clz: str = "config" if not isinstance(config_clz, str) else config_clz.strip()
    if not re.match(r"^config(\.[a-zA-Z0-9_]+)*$", config_clz):
        raise ValueError("Invalid config module name (e.g., config.prod)")
    raw_path: str = os.path.join(root_path, config_clz.replace(".", os.path.sep))
    config_path = Path(os.path.abspath(raw_path))  # 关键！消除符号和多余斜杠
    root_path_obj = Path(root_path).resolve()
    # 检查绝对路径是否在根目录下
    if not config_path.is_relative_to(root_path_obj):
        raise ValueError(f"Config path {config_path} is outside project root")
    try:
        # 仅允许加载 config 子目录下的模块
        module = importlib.import_module(f"{config_clz}", package="config")
        config = getattr(module, "config")
    except (ImportError, AttributeError) as e:
        console.error(f"Config module {config_clz} not found: {e}")
        sys.exit(1)
    config_toml: dict = {}
    base_config: dict = {}
    static_folder: Optional[str] = None
    template_folder: Optional[str] = None
    if not is_cli:
        toml_file: str = os.path.join(config_path, "config.toml")
        if not os.path.isfile(toml_file):
            console.error(u"config.toml not found!")
            sys.exit(0)
        config_toml = tomllib.load(
            codecs.open(toml_file, "r", "UTF-8").read())
        if not in_dict(config_toml, "config"):
            console.error(u"config.toml format error!")
            sys.exit(0)
        base_config = config_toml["config"]
        static_folder = get_args_from_dict(
            base_config, "static_folder", default="{root_path}/web/static")
        static_folder = static_folder.replace("{root_path}", root_path)
        static_folder = os.path.abspath(static_folder)
        if not os.path.isdir(static_folder):
            console.error(u"Static file path not found!")
            sys.exit(0)
        template_folder = get_args_from_dict(
            base_config, "template_folder", default="{root_path}/web/template")
        template_folder = template_folder.replace("{root_path}", root_path)
        template_folder = os.path.abspath(template_folder)
        if not os.path.isdir(template_folder):
            console.error(u"Template path not found!")
            sys.exit(0)
    config_name: str = "default" if not isinstance(config_name, str) else config_name
    config_name = config_name.lower()
    if not in_dict(config, config_name):
        console.error(u"Config invalid!")
        sys.exit(0)
    app: Flask = Flask(
        __name__, static_folder=static_folder, template_folder=template_folder)
    app.json_provider_class = MioJsonProvider
    app.json = MioJsonProvider(app)
    app.config.from_object(config[config_name])
    app.config["ENV"] = config_name
    config[config_name].init_app(app)
    babel = Babel(app)
    if in_dict(base_config, "csrf"):
        if is_enable(base_config["csrf"], "enable"):
            csrf = CSRFProtect()
            csrf.init_app(app)
    if is_enable(app.config, "MIO_MAIL"):
        from flask_mail import Mail
        mail = Mail()
        mail.init_app(app)
    if is_enable(app.config, "MONGODB_ENABLE"):
        db = MongoEngine()
        db.init_app(app)
        # ! 至少输出警告级别
        logging.getLogger('pymongo').setLevel(logging.WARN)
    if is_enable(app.config, "RDBMS_ENABLE"):
        rdb = SQLAlchemy()
        rdb.init_app(app)
    if is_enable(app.config, "CELERY_ENABLE"):
        celery_app_config: dict = {
            "broker": app.config["CELERY_BROKER_URL"],
            "backend": app.config["CELERY_BACKEND_URL"],
        }
        if "CELERY_RESULT_BACKEND" in app.config:
            celery_app_config.update({"result_backend": app.config["CELERY_RESULT_BACKEND"]})
        if "CELERY_RESULT_PERSISTENT" in app.config:
            celery_app_config.update({"result_persistent": app.config["CELERY_RESULT_PERSISTENT"]})
        if "CELERY_RESULT_EXCHANGE" in app.config:
            celery_app_config.update({"result_exchange": app.config["CELERY_RESULT_EXCHANGE"]})
        if "CELERY_RESULT_EXCHANGE_TYPE" in app.config:
            celery_app_config.update({"result_exchange_type": app.config["CELERY_RESULT_EXCHANGE_TYPE"]})
        if "CELERY_BROKER_USE_SSL" in app.config:
            celery_app_config.update({"broker_use_ssl": app.config["CELERY_BROKER_USE_SSL"]})
        celery_app = Celery(
            app.import_name,
            **celery_app_config
        )
        logging.getLogger('amqp').setLevel(log_level)
        logging.getLogger('celery').setLevel(log_level)
    if is_enable(app.config, "REDIS_ENABLE"):
        redis_db = FlaskRedis()
        redis_db.init_app(app)
    if is_enable(app.config, "CORS_ENABLE"):
        if not in_dict(app.config, "CORS_URI"):
            console.error(u"CORS_URI not define.")
            sys.exit(0)
        CORS(app, resources=app.config["CORS_URI"])
    if is_enable(app.config, "CACHED_ENABLE"):
        cache = Cache(app)
    if is_cli:
        # 如果是cli模式，这里就出去就行了
        return app, console
    blueprints_config: List[dict] = get_args_from_dict(config_toml, "blueprint", default=[])
    for blueprint in blueprints_config:
        key: str = list(blueprint.keys())[0]
        clazz = __import__(blueprint[key]["class"], globals(), fromlist=[key])
        bp: blueprints.Blueprint = getattr(clazz, key)
        if in_dict(blueprint[key], "url_prefix"):
            app.register_blueprint(bp, url_prefix=blueprint[key]["url_prefix"])
        else:
            app.register_blueprint(bp)

    @app.after_request
    def server_headers(response):
        response.headers["server"] = f"PyMIO/{MIO_SYSTEM_VERSION}"
        return response

    return app, console


def get_timezone_config() -> str:
    try:
        from config import Config
        tz: str = getattr(Config, "MIO_TIMEZONE")
        return tz
    except Exception as e:
        str(e)
        return "Asia/Shanghai"


def init_timezone():
    try:
        tz: str = get_timezone_config()
        os.environ["TZ"] = tz
        time.tzset()
    except Exception as e:
        str(e)


def init_uvloop():
    try:
        if os_name == "unknown":
            return
        if os_name == "windows":
            import winloop
            asyncio.set_event_loop_policy(winloop.EventLoopPolicy())
            winloop.install()
            return
        import uvloop
        if not isinstance(asyncio.get_event_loop_policy(), uvloop.EventLoopPolicy):
            uvloop.install()  # 等效于 asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            print("uvloop event loop policy activated")
    except Exception as e:
        str(e)


def get_logger_level(config_name: str) -> Tuple[int, LoggerType, bool]:
    config_name = config_name.replace("\"", "").replace("\"", "").lower()
    is_debug = False if config_name == "production" else True
    mio_logger_level: str = os.environ.get("MIO_LOGGER_LEVEL") or ""
    mio_logger_type: str = os.environ.get("MIO_LOGGER_TYPE") or ""
    log_level: Union[str, int] = logging.getLevelName(mio_logger_level)
    log_type: Optional[LoggerType] = nameToLevel.get(mio_logger_type)
    if not is_number(log_level):
        log_level = logging.INFO if config_name == "production" else logging.DEBUG
    if log_type is None:
        log_type = LoggerType.CONSOLE_FILE if config_name == "production" else LoggerType.CONSOLE
    return log_level, log_type, is_debug


def get_buffer_size() -> Tuple[Optional[int], Optional[int]]:
    max_buffer_size: Optional[Union[str, int]] = os.environ.get("MAX_BUFFER_SIZE") or ""
    max_body_size: Optional[Union[str, int]] = os.environ.get("MAX_BODY_SIZE") or ""
    max_buffer_size = None if not is_number(max_buffer_size) else int(max_buffer_size)
    max_body_size = None if not is_number(max_body_size) else int(max_body_size)
    return max_buffer_size, max_body_size


def get_cpu_limit() -> int:
    if os_name in ["windows", "unknown"]:
        # for windows os, just 1. test in win11
        return 1
    cpu_limit: int = 1 if not is_number(os.environ.get("MIO_LIMIT_CPU")) \
        else int(os.environ.get("MIO_LIMIT_CPU"))
    return cpu_limit
