# coding=utf-8
"""Interface to all RSA encrypt / decrypt functions"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class RSAKeyLoader(ABC):
    """General interface for classes that load RSA Keys"""

    @abstractmethod
    def load(self, source) -> None:
        """Loads from source (source can be self i.e. generated within class)"""

    @abstractmethod
    def modulus(self) -> int:
        """getter for modulus"""

    @abstractmethod
    def pub_exp(self) -> int:
        """Getter for e"""

    def priv_exp(self) -> int:
        """Getter for d"""

    # might need to do p and q as well for constant time mod exp


@dataclass
class RSAKeyFromFile(RSAKeyLoader):
    """Will load a key from a private key file"""

    modulus: Optional[int]   # n
    pub_exp: Optional[int]   # e
    priv_exp: Optional[int]  # d
    p: Optional[int]
    q: Optional[int]

    def load(self, path_to_private) -> str:
        """
        Loads from file given file path;
        """
        pass

    def parse(self):
        """Given loaded SSL info, parses and populates n, d, e, p, q """
        pass


@dataclass
class RSAKeyGenerator(RSAKeyLoader):
    """Generates keys, writes to file, loads in standard way"""


@dataclass
class RSAKey:
    """RSA Key pair; can verify RSA pair. Program does not deal with generation (v insecure in python)
    Outsource verifying to system (interest of security)"""

    def __init__(self, loader: RSAKeyLoader):

        _n = loader.modulus()
        _e = loader.pub_exp()
        _d = loader.priv_exp()

        # maybe expand to p & q

        self.public = [_n, _e]
        self.private = [_n, _d]

    def validate_keypair(self):
        """
        Ensures that keypair is valid
        Compare modulus of pub and priv; ensure MATCHING;
        """
        pass



