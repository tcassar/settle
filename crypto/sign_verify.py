# coding=utf-8
"""
RSA Sign/Verify classes
"""
import keys, hashes

from abc import ABC


class DecryptionError(Exception):
    "Failed to decrypt"


class RSA(ABC):
    """RSA methods; ABC so is never instantiated"""

    @staticmethod
    def encrypt(message: bytes, publicKey: keys.RSAPublicKey) -> :
        return pow(int(message), publicKey.e, publicKey.n)


    @staticmethod
    def naive_decrypt(ciphertext, privateKey: keys.RSAKey):
        # TODO: CRT decryption
        if privateKey is keys.RSAPublicKey:
            raise DecryptionError("Cannot decrypt with a public key")

        return pow(ciphertext, privateKey.d, privateKey.n)

    @staticmethod
    def sign(hash: hashes.Hash, ):
