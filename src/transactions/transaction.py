# coding=utf-8

"""
Handles transaction object
"""

import datetime
# coding=utf-8
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from src.crypto import keys, hashes, rsa


class TransactionError(Exception):
    ...


class VerificationError(Exception):
    ...


class Signable(ABC):
    """Base class for objects that can be signed; needs a hash implementation, cannot be added into ABC for reasons"""

    @abstractmethod
    def sign(self, key: keys.RSAPrivateKey, *, origin: str) -> None:
        ...

    @abstractmethod
    def hash(self) -> bytes:
        ...


@dataclass
class Transaction(Signable):
    src: int
    dest: int
    amount: int
    src_pub: keys.RSAPublicKey
    dest_pub: keys.RSAPublicKey
    ID: int = 0
    msg: str = ""
    time = datetime.datetime.now()
    signatures: dict[int, bytes] = field(default_factory=lambda: {})

    def hash(self) -> bytes:
        # standard way to produce hash using SHA256 interface from crypto lib
        return (
            hashes.Hasher(
                f"{self.src, self.dest, self.amount, self.msg, self.time}".encode(
                    "utf8", sys.byteorder
                )
            )
            .digest()
            .h
        )

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
            return sig

        # raise error if not given a priv key
        if (keytype := type(key)) is not keys.RSAPrivateKey:
            raise TransactionError(f"Was given a {keytype}, not an RSAPrivateKey")

        # initialise sigs dict if it doesn't already exist
        if not self.signatures:
            self.signatures = {self.src: b"", self.dest: b""}

        # accept origin as src or dest;
        # check for overwrite, raise error if case
        # append with key of ID to signatures dict
        if origin == "src":
            if not self.signatures[self.src]:  # check for overwrites
                self.signatures[self.src] = generate_signature(self)
            else:
                overwrite_err("src")  # handle overwrite err

        elif origin == "dest":
            if not self.signatures[self.dest]:
                self.signatures[self.dest] = generate_signature(self)
            else:
                overwrite_err("dest")

        else:
            # if parameter wasn't src or dest, raise error
            raise ValueError(f"{origin!r} not a valid parameter; use 'src' or 'dest'")

    def verify(self) -> None:
        """Raise verification error if invalid sig"""

        # ensure that transaction has its two signatures:
        try:
            for sig in [self.src, self.dest]:
                _ = self.signatures[sig]
        except KeyError:
            raise VerificationError(f'Has not been signed by USRID {sig}')

        # build list of keys to verif
        usr_keys = [self.src_pub, self.dest_pub]

        if not usr_keys:
            raise VerificationError("No valid keys were passed in")

        hash_from_obj: bytes = self.hash()

        for key, origin in zip(usr_keys, [self.src, self.dest]):
            hash_from_sig = rsa.RSA.inv_sig(self.signatures[origin], key)
            if hash_from_sig != hash_from_obj:
                raise VerificationError(f'{self.src} sig invalid')


