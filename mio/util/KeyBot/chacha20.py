# -*- coding: UTF-8 -*-
import inspect
from Crypto.Cipher import ChaCha20 as baseChaCha20
from Crypto.Random import get_random_bytes
from typing import Optional
from .base import BaseModel


class ChaCha20(BaseModel):
    _is_poly1305: bool = True
    _counter: int = 0

    def __init__(
            self, key: Optional[str] = None, iv: Optional[str] = None, aad: Optional[str] = None,
            is_hex: bool = False, **kwargs):
        """
        初始化加密函数
        :param key: 加密密钥，两种方式传入，hex或base64，不填则自动生成
        :param iv: nonce，两种方式传入，hex或base64，不填则自动生成
        """
        id(aad), id(kwargs)
        super().__init__(self.__class__.__name__)
        default_key: Optional[bytes] = None
        default_iv: Optional[bytes] = None
        if key is None or len(key) == 0:
            default_key = get_random_bytes(32)
        if iv is None or len(iv) == 0:
            default_iv = get_random_bytes(8)
        self.set_key(default_key, key=key, is_hex=is_hex)
        self.set_iv(default_iv, iv=iv, is_hex=is_hex)

    def encrypt(self, msg: bytes) -> Optional[bytes]:
        console_log = self.__get_logger__(inspect.stack()[0].function)
        try:
            cipher_encrypt = baseChaCha20.new(key=self._key, nonce=self._iv)
            cipher: bytes = cipher_encrypt.encrypt(msg)
            return cipher
        except Exception as e:
            console_log.error(e)
            return None

    def decrypt(self, cipher: bytes) -> Optional[bytes]:
        console_log = self.__get_logger__(inspect.stack()[0].function)
        try:
            cipher_decrypt = baseChaCha20.new(key=self._key, nonce=self._iv)
            plain: bytes = cipher_decrypt.decrypt(cipher)
            return plain
        except Exception as e:
            console_log.error(e)
            return None
