# -*- coding: UTF-8 -*-
import os
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.exceptions import InvalidSignature
from typing import Optional


class ECDSA(object):
    __key_path__: str
    __privkey__: Optional[ec.EllipticCurvePrivateKey] = None
    __pubkey__: Optional[ec.EllipticCurvePublicKey] = None

    def __init__(self, key_path: Optional[str] = None):
        self.__key_path = key_path
        if key_path and not os.path.isdir(key_path):
            os.makedirs(key_path)

    def gen_new_key(self, is_save: bool = True):
        """生成新的ECDSA密钥对"""
        self.__privkey__ = ec.generate_private_key(ec.SECP256R1())
        self.__pubkey__ = self.__privkey__.public_key()
        if is_save and self.__key_path:
            self._save_keys()

    def _save_keys(self):
        """保存密钥到文件"""
        privkey_file = f"{self.__key_path}/ecdsa_privkey.pem"
        pubkey_file = f"{self.__key_path}/ecdsa_pubkey.pem"

        # 保存私钥
        with open(privkey_file, "wb") as f:
            f.write(self.__privkey__.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # 保存公钥
        with open(pubkey_file, "wb") as f:
            f.write(self.__pubkey__.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

    def __load_key__(self, key_type: int):
        """加载密钥文件"""
        key_file = "ecdsa_privkey.pem" if key_type == 1 else "ecdsa_pubkey.pem"
        key_path = os.path.join(self.__key_path, key_file)

        if not os.path.isfile(key_path):
            return

        with open(key_path, "rb") as kf:
            data = kf.read()

        try:
            if key_type == 1:
                self.__privkey__ = serialization.load_pem_private_key(
                    data, password=None)
                self.__pubkey__ = self.__privkey__.public_key()
            else:
                self.__pubkey__ = serialization.load_pem_public_key(data)
        except ValueError:
            return

    def sign(self, message: str) -> Optional[str]:
        """签名消息"""
        if not self.__privkey__:
            self.__load_key__(1)
            if not self.__privkey__:
                return None

        signature = self.__privkey__.sign(
            message.encode("utf-8"),
            ec.ECDSA(SHA256())
        )
        return base64.b64encode(signature).decode("utf-8")

    def verify(self, message: str, signature: str) -> bool:
        """验证签名"""
        if not self.__pubkey__:
            self.__load_key__(0)
            if not self.__pubkey__:
                return False

        try:
            sig = base64.b64decode(signature)
            self.__pubkey__.verify(
                sig,
                message.encode("utf-8"),
                ec.ECDSA(SHA256())
            )
            return True
        except InvalidSignature:
            return False
        except Exception as e:
            print(e)
            return False

    # 密钥交换接口（保持与RSA模块一致）
    def get_base64_pubkey(self) -> Optional[str]:
        if not self.__pubkey__:
            self.__load_key__(0)
        if self.__pubkey__:
            pem = self.__pubkey__.public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return base64.b64encode(pem).decode("utf-8")
        return None

    def get_base64_privkey(self) -> Optional[str]:
        if not self.__privkey__:
            self.__load_key__(1)
        if self.__privkey__:
            pem = self.__privkey__.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            return base64.b64encode(pem).decode("utf-8")
        return None

    def set_base64_pubkey(self, crypto: str):
        pem = base64.b64decode(crypto)
        self.__pubkey__ = serialization.load_pem_public_key(pem)

    def set_base64_privkey(self, crypto: str):
        pem = base64.b64decode(crypto)
        self.__privkey__ = serialization.load_pem_private_key(
            pem, password=None)
        self.__pubkey__ = self.__privkey__.public_key()

    def get_pubkey(self) -> Optional[bytes]:
        if self.__pubkey__:
            return self.__pubkey__.public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo
            )
        return None

    def get_privkey(self) -> Optional[bytes]:
        if self.__privkey__:
            return self.__privkey__.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        return None

    def set_pubkey(self, crypto_message: bytes):
        self.__pubkey__ = serialization.load_pem_public_key(crypto_message)

    def set_privkey(self, crypto_message: bytes):
        self.__privkey__ = serialization.load_pem_private_key(
            crypto_message, password=None)
        self.__pubkey__ = self.__privkey__.public_key()
