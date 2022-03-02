# coding=utf-8
import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass

import crypto.rsa


class Signable(ABC):
    """Base class for objects that can be signed"""

    @abstractmethod
    def add_sig(self, sig: bytes):
        ...

    @abstractmethod
    def __hash__(self):
        ...


@dataclass
class User:
    """for users from db"""


@dataclass
class NewTransaction(Signable):

    src: User
    dest: User
    amount: int
    ID = 0
    msg: str = ""
    time = datetime.datetime.now()

    def __hash__(self):
        hash(f'{self.src, self.dest, self.amount, self.ID, self.msg, self.time}')
