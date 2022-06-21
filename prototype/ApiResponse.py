# -*- coding: utf-8 -*-
import orjson as json
from flask import make_response
from flask.wrappers import Response
from typing import Any, Optional, Dict


class ApiResponse(object):
    code: int
    description: str
    data: Any

    def __init__(self, code: int, description: Optional[str] = None, data: Any = ''):
        self.code = code
        description = u'操作完成' if description is None else str(description).strip()
        self.description = description
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        if self.data is None:
            self.data = ''
        static_type_list = [str, int, float, dict, list]
        is_clazz = True
        for static_type in static_type_list:
            if isinstance(self.data, static_type):
                is_clazz = False
                break
        if not is_clazz:
            data = self.data
        else:
            # 调用具体原型的to_dict
            clazz = self.data
            data = clazz.to_dict()
        jd: Dict[str, Any] = {
            'code': self.code,
            'description': self.description,
            'data': data
        }
        return jd

    def to_jsonify(self) -> Response:
        headers: Dict[str, str] = {
            'content-type': 'application/json'
        }
        respone: Response = make_response(json.dumps(self.to_dict()))
        respone.headers = headers
        return respone
