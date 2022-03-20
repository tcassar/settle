# coding=utf-8
import datetime
from dataclasses import dataclass


@dataclass
class User:
    name: str
    email: str
    modulus: str
    pub_exp: str
    password: str = "default"
    id: int = 0

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
        return f"Group(name={self.name}, id={self.id})"

    def __str__(self):
        return f"Group:\n\tName: {self.name}, ID = {self.id}"


@dataclass
class GroupLink:
    id: int
    group_id: int
    usr_id: int


@dataclass
class GroupList:
    groups: list[Group]

    def __str__(self):
        out = ""
        for group in self.groups:
            out += f"{str(group)}\n"

        return out


@dataclass
class PrettyTransaction:
    id: int
    group: int
    amount: int
    time: str
    reference: str
    other: str
    verified: bool

    def __str__(self):
        return f'{self.src} owes {self.dest} £{round(self.amount / 100, 2):02}' \
               f'\nReference: {self.reference}' \
               f'\nAgreed upon at {self.time}'


@dataclass
class PrettyList:
    src_list: list[PrettyTransaction]
    dest_list: list[PrettyTransaction]