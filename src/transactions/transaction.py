# coding=utf-8

"""
Handles transaction object
"""

# coding=utf-8
import sys

from src.crypto import keys, hashes, rsa

import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


class LedgerBuildError(Exception):
    """Error building ledger"""


class TransactionError(Exception):
    ...


class VerificationError(Exception): ...


class Signable(ABC):
    """Base class for objects that can be signed; needs a hash implementation, cannot be added into ABC for reasons"""

    @abstractmethod
    def sign(self, key: keys.RSAPrivateKey, *, origin: str) -> None:
        ...

    @abstractmethod
    def hash(self) -> bytes: ...


@dataclass
class Transaction(Signable):
    src: int
    dest: int
    amount: int
    ID = 0
    msg: str = ""
    time = datetime.datetime.now()
    signatures: dict[int, bytes] = field(default_factory=lambda: {})

    def hash(self) -> bytes:
        # standard way to produce hash using SHA256 interface from crypto lib
        return hashes.Hasher(f"{self.src, self.dest, self.amount, self.msg, self.time}".encode('utf8', sys.byteorder)).digest().h

    # IMPORTANT: CANNOT USE DUNDER HASH AS PYTHON DOES WEIRD HASH COMPRESSION
    def __hash__(self):
        raise NotImplementedError("__hash__ cannot be used, used .hash() method")

    def sign(self, key: keys.RSAPrivateKey, *, origin: str) -> None:

        def overwrite_err(where: str) -> None:
            """Helper to raise overwrite error"""
            raise TransactionError(f"Cannot overwrite signature of {where}")

        def generate_signature(obj: Transaction) -> bytes:
            """Helper to generate a signature of the object"""
            sig = rsa.RSA.sign(obj.hash(), key)
            print(sig)
            return sig

        # raise error if not given a priv key
        if (keytype := type(key)) is not keys.RSAPrivateKey:
            raise TransactionError(f'Was given a {keytype}, not an RSAPrivateKey')

        # initialise sigs dict if it doesn't already exist
        if not self.signatures:
            self.signatures = {self.src: b'', self.dest: b''}

        # accept origin as src or dest;
        # check for overwrite, raise error if case
        # append with key of ID to signatures dict
        if origin == 'src':
            if not self.signatures[self.src]:  # check for overwrites
                self.signatures[self.src] = generate_signature(self)
            else:
                overwrite_err('src')  # handle overwrite err

        elif origin == 'dest':
            if not self.signatures[self.dest]:
                self.signatures[self.dest] = generate_signature(self)
            else:
                overwrite_err('dest')

        else:
            # if parameter wasn't src or dest, raise error
            raise ValueError(f'{origin!r} not a valid parameter; use \'src\' or \'dest\'')

    def verify_sig(self, *, src: keys.RSAPublicKey = None, dest: keys.RSAPublicKey=None) -> None:
        """Raise verification error if invalid sig"""

        # build list of keys to verif
        passed_keys = [key for key in [src, dest] if type(key) is keys.RSAPrivateKey or type(key) is keys.RSAPublicKey]

        if not passed_keys:
            raise VerificationError('No valid keys were passed in')

        hash_from_obj: bytes = self.hash()

        # verify src
        if src:
            # decrypt src signature
            src_from_sig: bytes = rsa.RSA.inv_sig(self.signatures[self.src], src)
            if src_from_sig != hash_from_obj:
                raise VerificationError(f'Signature doesn\'t match hash for USER ID: {self.src}')

        # verify dest
        if dest:
            # decrypt dest signature
            dest_from_sig: bytes = rsa.RSA.inv_sig(self.signatures[self.dest], dest)
            if dest_from_sig != hash_from_obj:
                raise VerificationError(f'Signature doesn\'t match hash for USER ID: {self.dest}')


@dataclass
class Ledger:
    """Multiple transactions contained to one group (assumed from building);
     built from a stream of transaction objects"""

    # ledger, big list of transactions;
    # TODO: maybe make ledger generator
    ledger: list[Transaction] = field(default_factory=lambda: [])

    def __bool__(self):
        """False if ledger empty"""
        return not not self.ledger

    def append(self, transaction: Transaction) -> list[Transaction]:
        """Nice syntax for adding transactions to ledger"""
        print(type(transaction))

        if type(transaction) is not Transaction:
            raise LedgerBuildError(f'cannot append type {transaction} to ledger; must be transaction')
        else:
            self.ledger.append(transaction)

        return self.ledger

    def _verify_transactions(self):
        """Verifies the keys of all the transactions in the group.
        Raises error if a faulty transaction is found"""
