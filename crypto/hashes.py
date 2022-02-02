# coding=utf-8

"""
Simple RSA implementation for signing / verifying digital signatures.
Will have side channel vulnerabilities due to the way that Python stores numbers
Hashing is done through hashlib library
"""

import hashlib
import sys
from dataclasses import dataclass


class HashError(Exception):
    """Hash provided is not in valid format"""


class HasherError(Exception):
    ...


@dataclass
class Hash:
    def __init__(self, h: bytes):
        self.validate(h)
        self.h: bytes = h

    def int_digest(self) -> int:
        # int representation of bytes, not actual value
        return int.from_bytes(self.h, byteorder=sys.byteorder)

    @staticmethod
    def validate(passed_hash):
        try:
            assert len(passed_hash) == 32  # 256 / 8
            assert type(passed_hash) == bytes
        except AssertionError:
            raise HashError("Hash was not in the form of a hash")


class Hasher:
    """Interface to hashing; for consistency always use SHA256,"""

    @staticmethod
    def _validate(inp):
        """Raises HasherError if input isn't bytes"""
        if type(inp) is not bytes:
            raise HasherError(
                f"Type passed into _hasher was not bytes; received {type(inp)}"
            )

    def __init__(self, initial: bytes = b"") -> None:
        self._validate(initial)
        self._hasher = hashlib.sha3_256(initial)

    def update(self, msg: bytes) -> None:
        """Updates _hasher with given message after checking that message was in fact bytes"""
        self._validate(msg)
        self._hasher.update(msg)

    def digest(self) -> Hash:
        """Digests current hash; digests always returns a Hash object"""
        return Hash(self._hasher.digest())
