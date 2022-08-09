# -*- coding: UTF-8 -*-
import os
import jwt
import inspect
from typing import Optional, Dict, Any
from mio.util.Helper import get_root_path, get_variable_from_request, read_txt_file
from mio.util.Logs import LogHandler


class JwtHelper(object):
    VERSION = '0.1'
    ALGORITHM: str = "HS256"
    PRIVATE_KEY: Optional[str] = None
    PUBLIC_KEY: Optional[str] = None
    VERIFY_EXP: bool = False

    def __get_logger__(self, name: str) -> LogHandler:
        name = f"{self.__class__.__name__}.{name}"
        return LogHandler(name)

    def __init__(
            self, algorithm: str = "HS256", private_key: Optional[str] = None, public_key: Optional[str] = None,
            verify_exp: bool = False, nbits: int = 512
    ):
        if algorithm == "RS256":
            if private_key is None or public_key is None:
                from mio.util.KeyBot import KeyBot
                key_path: str = os.path.join(get_root_path(), "jwt_key")
                # 注意：默认长度是2048，因此建议在启动之前，先运行一个cli来生成密钥对或是把生成好的秘钥对直接放进去
                key_bot = KeyBot(key_path)
                public_key = key_bot.get_base64_pubkey()
                private_key = key_bot.get_base64_privkey()
                if public_key is None or private_key is None:
                    key_bot.gen_new_key(nbits=nbits)
                private_key = read_txt_file(os.path.join(key_path, "privkey.pem"))
                public_key = read_txt_file(os.path.join(key_path, "cacert.pem"))
            if len(private_key) == 0 or len(public_key) == 0:
                raise "public/private key can not be null."
            self.PRIVATE_KEY = private_key
            self.PUBLIC_KEY = public_key
        elif algorithm == "HS256":
            if private_key is None:
                from flask import current_app
                private_key = current_app.config["SECRET_KEY"]
            if len(private_key) == 0:
                raise "private key can not be null."
            self.PRIVATE_KEY = private_key
        else:
            raise 'algorithm must be "HS256" or "RS256".'
        self.ALGORITHM = algorithm
        self.VERIFY_EXP = verify_exp

    def encode(self, payload: Dict[str, Any]) -> Optional[str]:
        console_log = self.__get_logger__(inspect.stack()[0].function)
        try:
            return jwt.encode(payload, key=self.PRIVATE_KEY, algorithm=self.ALGORITHM)
        except Exception as e:
            console_log.error(e)
            return None

    def decode(self, encode: str) -> Optional[Dict[str, Any]]:
        console_log = self.__get_logger__(inspect.stack()[0].function)
        try:
            options: Optional[Dict] = {"verify_exp": self.VERIFY_EXP}
            if self.ALGORITHM == "RS256":
                return jwt.decode(encode, key=self.PUBLIC_KEY, algorithms=self.ALGORITHM, options=options)
            if self.ALGORITHM == "HS256":
                return jwt.decode(encode, key=self.PRIVATE_KEY, algorithms=self.ALGORITHM, options=options)
            return None
        except jwt.ExpiredSignatureError:
            console_log.debug("Signature has expired")
            return None
        except Exception as e:
            console_log.error(e)
            return None

    def get_info(self) -> Optional[Dict[str, Any]]:
        console_log = self.__get_logger__(inspect.stack()[0].function)
        authorization: str = get_variable_from_request("Authorization", method="header", force_str=True)
        if len(authorization) == 0:
            console_log.debug("Authorization is Null.")
            return None
        if not authorization.startswith("JWT"):
            console_log.debug("Authorization not JWT.")
            return None
        *_, encode = authorization.split(" ")
        data: Optional[Dict[str, Any]] = self.decode(encode)
        if data is None:
            console_log.error("JWT decode fail.")
        return data
