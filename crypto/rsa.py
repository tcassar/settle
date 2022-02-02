# coding=utf-8
"""
RSA Sign/Verify classes
"""

from crypto import keys, hashes

from abc import ABC
from dataclasses import dataclass
from math import ceil
import re
import sys


class DecryptionError(Exception):
    "Failed to decrypt"


class SignatureError(Exception):
    ...


class RSA(ABC):
    """RSA methods; ABC so is never instantiated; just used for namespacing"""

    @staticmethod
    def _check_private_key(key) -> None:
        if type(key) == keys.RSAPublicKey:
            raise DecryptionError("Cannot decrypt with a public key")

    @staticmethod
    def int_to_bytes(n: int) -> bytes:
        return int.to_bytes(n, length=n.bit_length(), byteorder=sys.byteorder).rstrip(b'\x00')

    @staticmethod
    def bytes_to_str(b: bytes) -> str:
        # TODO: Understand why this isn't working don't just delete redundant bytes
        return b.decode("utf8").replace("\x00", "")

    @staticmethod
    def encrypt(message: bytes, publicKey: keys.RSAPublicKey) -> bytes:
        message = int.from_bytes(message, sys.byteorder)
        cipher = pow(message, publicKey.e, publicKey.n)

        # TODO: figure out what length means
        return RSA.int_to_bytes(cipher)

    @staticmethod
    def naive_decrypt(ciphertext: bytes, privateKey: keys.RSAKey) -> bytes:
        # TODO: CRT decryption

        RSA._check_private_key(privateKey)

        ciphertext = int.from_bytes(ciphertext, sys.byteorder)
        plaintext = pow(ciphertext, privateKey.d, privateKey.n)

        return RSA.int_to_bytes(plaintext)

    @staticmethod
    def sign(msg: bytes, key: keys.RSAKey) -> bytes:
        # check we have a private key
        RSA._check_private_key(key)
        msg = int.from_bytes(msg, sys.byteorder)
        cipher = pow(msg, key.d, key.n)

        return RSA.int_to_bytes(cipher)

    @staticmethod
    def de_sig(sig: bytes, key: keys.RSAPublicKey) -> bytes:
        print(type(sig))
        sig = int.from_bytes(sig, sys.byteorder)
        de_sig = pow(sig, key.e, key.n)
        return RSA.int_to_bytes(de_sig)



class Signature: ...


class Sigscheme(ABC):
    """Simplest interface possible to sign with"""

    @staticmethod
    def sign(message: str, key: keys.RSAKey):
        # turn the message into bytes
        b_msg: bytes = message.encode("utf8")

        # encrypt with private key

    @staticmethod
    def verify(message: str, signature: Signature):
        ...
