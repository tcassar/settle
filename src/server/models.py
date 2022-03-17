# coding=utf-8
from dataclasses import dataclass


@dataclass
class User:
    name: str
    email: str
    modulus: str
    pub_exp: str
    password: str = "default"

    def __str__(self):
        return f"""\nName:\t{self.name}
Email:\t{self.email}
Modulus:\t{self.modulus},
Public Exponent:\t{self.pub_exp}
                """


@dataclass
class Group:
    id: int
    name: str
    password: str

    def __repr__(self):
        return f"Group({self.name}, {self.password})"
