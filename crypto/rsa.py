# coding=utf-8
"""
RSA Sign/Verify classes
"""

from crypto import keys, hashes

from abc import ABC
from math import ceil
import sys


class DecryptionError(Exception):
    "Failed to decrypt"


class RSA(ABC):
    """RSA methods; ABC so is never instantiated; just used for namespacing"""

    @staticmethod
    def int_to_bytes(n: int) -> bytes:
        return int.to_bytes(n, length=ceil(n.bit_length()), byteorder=sys.byteorder)

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
        if type(privateKey) == keys.RSAPublicKey:
            raise DecryptionError("Cannot decrypt with a public key")

        ciphertext = int.from_bytes(ciphertext, sys.byteorder)
        plaintext = pow(ciphertext, privateKey.d, privateKey.n)

        return RSA.int_to_bytes(plaintext)

    @staticmethod
    def sign(hash: hashes.Hash, private: keys.RSAKey) -> bytes:
        ...
