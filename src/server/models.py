# coding=utf-8
from dataclasses import dataclass


@dataclass
class User:
    name: str
    email: str
    modulus: bytes
    pub_exp: bytes
