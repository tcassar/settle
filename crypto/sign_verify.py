# coding=utf-8
"""
RSA Sign/Verify classes
"""
import crypto.keys

from abc import ABC


class RSA(ABC):
    """RSA methods; ABC so is never instantiated"""

    @staticmethod
    def encrypt(message: int, publicKey: keys.):
