# coding=utf-8
"""
RSA Sign/Verify classes
"""

from __future__ import annotations

import sys
from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.crypto import keys, hashes

if TYPE_CHECKING:
    from src.transactions.transaction import Signable


class DecryptionError(Exception):
    """Failed to decrypt"""


class SigningError(Exception):
    ...


class RSA(ABC):
    """RSA methods; ABC so is never instantiated; just used for namespacing"""

    @staticmethod
    def check_private_key(key) -> None:
        if type(key) == keys.RSAPublicKey:
            raise DecryptionError("Cannot decrypt with a public key")

    @staticmethod
    def int_to_bytes(n: int) -> bytes:
        return int.to_bytes(n, length=n.bit_length(), byteorder=sys.byteorder).rstrip(
            b"\x00"
        )

    @staticmethod
    def bytes_to_str(b: bytes) -> str:
        return b.decode("utf8").replace("\x00", "")

    @staticmethod
    def encrypt(message: bytes, publicKey: keys.RSAPublicKey) -> bytes:
        message = int.from_bytes(message, sys.byteorder)
        cipher = pow(message, publicKey.e, publicKey.n)

        return RSA.int_to_bytes(cipher)

    @staticmethod
    def naive_decrypt(ciphertext: bytes, privateKey: keys.RSAPrivateKey) -> bytes:
        # TODO: CRT decryption

        RSA.check_private_key(privateKey)

        ciphertext = int.from_bytes(ciphertext, sys.byteorder)
        plaintext = pow(ciphertext, privateKey.d, privateKey.n)

        return RSA.int_to_bytes(plaintext)

    @staticmethod
    def sign(msg: bytes, key: keys.RSAPrivateKey) -> bytes:
        # check we have a private key
        RSA.check_private_key(key)
        msg = int.from_bytes(msg, sys.byteorder)
        cipher = pow(msg, key.d, key.n)

        return RSA.int_to_bytes(cipher)

    @staticmethod
    def inv_sig(sig: bytes, key: keys.RSAPublicKey) -> bytes:
        """Will produce what was originally fed into sign() using public key"""

        sig = int.from_bytes(sig, sys.byteorder)
        de_sig = pow(sig, key.e, key.n)

        return RSA.int_to_bytes(de_sig)


class RestrictedNotary:
    """Can only verify with a given public key cannot sign"""

    def __init__(self, key: keys.RSAPublicKey):
        self.key = key

    def verify_object(self, obj: Signable) -> None:
        sig = obj.signature

        # make sure object is signed
        if not sig:
            raise SigningError("Object has no signature to verify")

        # calculate hash of the object
        h = hashes.Hasher(str(obj).encode("utf8")).digest().h

        # generate what the int representation of the hash (bytes) should have been
        h_ = RSA.inv_sig(sig, self.key)

        if h != h_:
            raise SigningError("Signature for object is invalid")


@dataclass
class Notary(RestrictedNotary):
    """Simplest interface possible to sign with"""

    key: keys.RSAPrivateKey

    def sign_object(self, obj: Signable) -> Signable:
        """Will sign an object; returns object, having added a signature"""

        # create byte representation of object
        msg = str(obj).encode("utf8")

        # hash the msg
        msg = hashes.Hasher(msg).digest().h

        # get signature of object
        sig: bytes = RSA.sign(msg, self.key)

        # append signature to object
        obj.add_sig(sig)

        # make sure signature is valid
        self.verify_object(obj)
        return obj