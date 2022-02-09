# coding=utf-8
from abc import ABC, abstractmethod

import crypto.keys


class Signable(ABC):
    """Base class for objects that can be signed"""

    @abstractmethod
    def __init__(self):
        self.signature: None | bytes = None
        ...

    @abstractmethod
    def add_sig(self, sig: bytes):
        ...

    @abstractmethod
    def __str__(self):
        ...
