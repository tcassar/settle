# coding=utf-8
"""
RSA Sign/Verify classes
"""
import keys
import hashes
from dataclasses import dataclass
from abc import abstractmethod, ABC


@dataclass
class Signature:
    s: int


class RSA(ABC):

    @classmethod
    @abstractmethod
    def sign(cls, message: hashes.Hash, key: keys.RSABaseKey) -> Signature:
        """Signs a message"""
        return Signature(cls._mod_exp(message.h, key.privateExponent, key.modulus))

    @staticmethod
    @abstractmethod
    def verify(s: Signature, key: keys.RSABaseKey) -> bool:
        """Checks if a signature matches a public key"""

    @staticmethod
    @abstractmethod
    def _mod_exp(base: int, exp: int, modulus: int) -> int:
        return pow(base, exp, modulus)
