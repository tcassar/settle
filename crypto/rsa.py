# coding=utf-8
"""
RSA Sign/Verify classes
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from crypto import keys, hashes

from abc import ABC
from dataclasses import dataclass
import sys


if TYPE_CHECKING:
    from transactions.transaction import Signable


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
        # TODO: Understand why this isn't working don't just delete redundant bytes
        return b.decode("utf8").replace("\x00", "")

    @staticmethod
    def encrypt(message: bytes, publicKey: keys.RSAPublicKey) -> bytes:
        message = int.from_bytes(message, sys.byteorder)
        cipher = pow(message, publicKey.e, publicKey.n)

        # TODO: figure out what length means
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


@dataclass
class Notary:
    """Simplest interface possible to sign with"""

    private_key: keys.RSAPrivateKey

    def sign_object(self, obj: Signable) -> Signable:
        """Will sign an object; returns object, having added a signature"""

        # create byte representation of object
        msg = str(obj).encode('utf8')

        # hash the msg
        msg = hashes.Hasher(msg).digest().h

        # get signature of object
        sig: bytes = RSA.sign(msg, self.private_key)

        # append signature to object
        obj.add_sig(sig)

        # make sure signature is valid
        if not self.verify_object(obj):
            raise SigningError(f"Valid Signature of {obj} could not be produced")

        return obj

    def verify_object(self, obj: Signable):
        sig = obj.signature

        # make sure object is signed
        if not sig:
            raise SigningError("Object has no signature to verify")

        # calculate hash of the object
        h = hashes.Hasher(str(obj).encode('utf8')).digest().h

        # generate what the int representation of the hash (bytes) should have been
        h_ = RSA.inv_sig(sig, self.private_key)

        return h == h_
