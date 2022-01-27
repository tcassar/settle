# coding=utf-8

"""
Simple RSA implementation for signing / verifying digital signatures.
Will have side channel vulnerabilities due to the way that Python stores numbers
Hashing is done through hashlib library
"""

import hashlib
from dataclasses import dataclass


class HashError(Exception):
    """Hash provided is not in valid format"""


class HasherError(Exception):
    """Hasher didn't like that"""


@dataclass
class Hash:
    """Hash; implemented for typehinting. Stores a str; should be hex number"""

    def __init__(self, h: int):
        self.h = h
        self.is_hash()

    def is_hash(self):
        """check that hash is valid format"""
        if type(self.h) is not int:
            raise HashError
        if self.h.bit_length() > 256 or self.h.bit_length() < 240:
            # TODO: Find out why hashes arent always 256; fairly annoying
            raise HashError


class Hasher:
    """Interface to hashing; for consistency always use SHA256,"""

    @staticmethod
    def _validate(inp):
        """Raises HasherError if input isn't bytes"""
        if type(inp) is not bytes:
            raise HasherError(f"Type passed into _hasher was not bytes but {type(inp)}")

    def __init__(self, initial: bytes = b"") -> None:
        self._validate(initial)
        self._hasher = hashlib.sha3_256(initial)

    def update(self, msg: bytes) -> None:
        """Updates _hasher with given message after checking that message was in fact bytes"""
        self._validate(msg)
        self._hasher.update(msg)

    def digest(self) -> Hash:
        """Digests current hash; digests always returns a Hash object"""
        hexd: str | int = self._hasher.hexdigest()
        # convert to an int
        hexd = int(hexd, 16)  # hashlib does not do hex prefix in str thus no slicing

        return Hash(hexd)
