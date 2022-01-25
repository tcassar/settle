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
    """Interface to hashing; for consistency always use SHA256, """

    def __init__(self, initial: bytes = b'') -> None:
        pass

    def update(self, msg: bytes) -> None:
        pass

    def digest(self) -> Hash:
        """Digests current hash; digests always returns a Hash object """
        pass