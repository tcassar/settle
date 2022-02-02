# coding=utf-8
"""Interface to all RSA encrypt / decrypt functions"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import os.path
import re
import subprocess


class RSAKeyError(Exception):
    """Problem with RSA Key"""


class RSAParserError(Exception):
    """Error in parsing file containing key"""


@dataclass
class RSABaseKey(ABC):
    """General interface for classes that load RSA Keys"""

    @abstractmethod
    def load(self, source) -> str:
        """Loads from source (source can be self i.e. generated within class)"""

    @abstractmethod
    def parse(self, loaded_key: str) -> None:
        """Parses information from source"""

    @abstractmethod
    def __getattr__(self, item):
        """Define getattr so can parse into dict, store dict, pull from dict as if attr"""


@dataclass
class RSAPublicKey(RSABaseKey, ABC):
    """Public key stuff"""


# noinspection SpellCheckingInspection
@dataclass
class RSAFileKey(RSABaseKey):
    """Will load a key from a private key file"""

    # initialise what we need, don't pass in anything at instantiation
    lookup: dict[str:int] | None = None
    key: None | str = None

    def _exists(self, item) -> bool:
        """Returns an attribute if it exists else raise an RSAKeyError"""
        if self.lookup is not None:
            if self.lookup[item] is not None:
                return True
        else:
            raise RSAKeyError("Requested attribute not found; have you parsed a key?")

    def load(self, path_to_private_key: str) -> str:
        """
        Loads PEM private key from file in file path;
        """

        # will only attempt to load if file exists
        if os.path.exists(path_to_private_key):
            key = str(
                subprocess.check_output(
                    f"openssl rsa -noout -text < {path_to_private_key}", shell=True
                )
            )
        else:
            raise RSAParserError('File not found')

        # strip into long easily parsable str; => remove spaces, newlines, colons
        key = key.replace(" ", "").replace("\\n", "").replace(":", "")

        # converted from bytes so remove b' ' with slice
        key = key[2:-1]

        # split after title section, discard info
        # pub exp is given in bin in text format; breaks splitting header with )
        key = re.sub(r"\(0x[0|1]*\)", "", key)  # matches of the form (0x[0|1]*)
        head, key = key.split(")")

        if head != "RSAPrivate-Key(2048bit,2primes":
            raise RSAParserError("File not in correct format")

        self.key = key
        return key

    # TODO: Handle parsing errors may be a good idea
    def parse(self, keys: str | None = None) -> None:
        """Given loaded SSL info, parses and populates n, d, e, p, q"""

        def hexstr_to_int(hexstr: str) -> int:
            # deals with exception pub exp which is always a decimal
            return int(hexstr) if re.fullmatch("[0-9]+", hexstr) else int(hexstr, 16)

        # use local key if key not given
        if keys is None:
            keys = self.key

        # set up delimiters; tells us to split when parsing
        delimiters = "modulus|publicExponent|privateExponent|prime1|prime2|exponent1|exponent2|coefficient".split(
            "|"
        )

        # split into a list along delimiters
        keys = re.sub(
            "modulus|publicExponent|privateExponent|prime1|prime2|exponent1|exponent2|coefficient",
            " ",
            keys,
        )
        keys = map(hexstr_to_int, keys.split())

        # combine to dict
        self.lookup = {label: key for label, key in zip(delimiters, keys)}

    def __getattr__(self, item: str) -> int:
        """
        Accepted items:
            modulus
            publicExponent
            privateExponent
            prime1
            prime2
            exponent1
            exponent2
            coefficient
        """
        if self._exists(item):
            return self.lookup[item]


@dataclass
class RSADatabaseKey(RSAPublicKey):
    """Loads a key from database
    WILL BE PUB KEY; not an issue, probably"""
