# coding=utf-8
"""Interface to all RSA encrypt / decrypt functions"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
import re
import subprocess


class RSAKeyError(Exception):
    """Problem with RSA Key"""


@dataclass
class RSAKeyLoader(ABC):
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
class RSAKeyFromFile(RSAKeyLoader):
    """Will load a key from a private key file"""

    # initialise what we need, don't pass in anything at instantiation
    lookup: dict[str:int] | None = None
    key: None | str = None

    @staticmethod
    def _exists(attr):
        """Returns an attribute if it exists else raise an RSAKeyError"""
        if type(attr) is int:
            return attr
        else:
            raise RSAKeyError("Requested attribute not found; have you parsed a key?")

        pass

    def load(self, path_to_private_key) -> str:
        """
        Loads PEM private key from file in file path;
        """

        key = str(
            subprocess.check_output(
                f"openssl rsa -noout -text < {path_to_private_key}", shell=True
            )
        )

        # strip into long easily parsable str; => remove spaces, newlines, colons
        key = key.replace(" ", "").replace("\\n", "").replace(":", "")

        # converted from bytes so remove b' ' with slice
        key = key[2:-1]

        # split after title section, discard info
        # pub exp is given in bin in text format; breaks splitting header with )
        key = re.sub(r"\(0x[0|1]*\)", "", key)  # matches of the form (0x[0|1]*)
        key = key.split(")")[1]

        self.key = key
        return key

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
        print(keys)

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
        return self.lookup[item]

