# -*- coding: utf-8 -*-
import sys
import inspect
from mio.util.Logs import LogHandler


class Daemon(object):
    def __get_logger__(self, name: str) -> LogHandler:
        name = f"{self.__class__.__name__}.{name}"
        return LogHandler(name)

    def hello(self, app, kwargs):
        id(app), id(kwargs)
        console_log: LogHandler = self.__get_logger__(inspect.stack()[0].function)
        sys_ver = sys.version
        console_log.info(f"Powered by PyMio.\nPython: {sys_ver}")
