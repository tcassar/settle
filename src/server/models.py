# coding=utf-8
import sys
from dataclasses import dataclass


@dataclass
class User:
    name: str
    email: str
    modulus: str
    pub_exp: bytes
    password: bytes = b''

    def __str__(self):
        return f"""Name: {self.name}
Email: {self.email}
Modulus: {self.modulus},
Public Exponent: {self.pub_exp}
                """

