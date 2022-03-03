# coding=utf-8
import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass


class Signable(ABC):
    """Base class for objects that can be signed"""

    @abstractmethod
    def add_sig(self, sig: bytes):
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
        hash(f"{self.src, self.dest, self.amount, self.ID, self.msg, self.time}")

    def add_sig(self, sig: bytes):
        ...
