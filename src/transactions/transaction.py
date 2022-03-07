# coding=utf-8

"""
Handles transaction object
"""

# coding=utf-8

from src.crypto import keys

import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass


class Signable(ABC):
    """Base class for objects that can be signed; needs a hash implementation, cannot be added into ABC for reasons"""

    @abstractmethod
    def sign(self, sig: bytes):
        ...


@dataclass
class Transaction(Signable):

    src: int
    dest: int
    amount: int
    ID = 0
    msg: str = ""
    time = datetime.datetime.now()

    def __hash__(self):
        # standard way to pro
        hash(f"{self.src, self.dest, self.amount, self.ID, self.msg, self.time}")

    def sign(self, sig: bytes) -> None:
        ...

    def verify_sig(self, public: keys.RSAPublicKey) -> None:
        """Raise verification error if invalid sig"""
