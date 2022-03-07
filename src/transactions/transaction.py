# coding=utf-8

"""
Handles transaction object
"""

# coding=utf-8

from src.crypto import keys

import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


class LedgerBuildError(Exception):
    """Error building ledger"""


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


@dataclass
class Ledger:
    """Multiple transactions contained to one group; built from a stream of transaction objects"""
    # ledger, big list of transactions;
    # TODO: maybe make ledger generator
    ledger: list[Transaction] = field(default_factory=lambda: [])

    def __bool__(self):
        """False if ledger empty"""
        return not not self.ledger

    def append(self, transaction: Transaction) -> list[Transaction]:
        """Nice syntax for adding transactions to collection"""
        print(type(transaction))

        if type(transaction) is not Transaction:
            raise LedgerBuildError(f'cannot append type {transaction} to ledger; must be transaction')
        else:
            self.ledger.append(transaction)

        return self.ledger

