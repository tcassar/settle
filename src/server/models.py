# coding=utf-8
from dataclasses import dataclass

import click


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

    def secho(self):
        click.secho("\n----")
        click.secho(f"Transaction ID = {self.id}\nGroup: {self.group}", bold=True)
        click.secho(f"{self.other}, £{(int(self.amount) / 100):.2f}", fg="blue")
        click.secho(self.reference)
        click.secho(f"at {self.time}")

        if self.verified:
            click.secho("Verified: True\n", fg="green")

        else:
            click.secho("Verified: False\n", fg="red", blink=True, bold=True)


@dataclass
class PrettyList:
    src_list: list[PrettyTransaction]
    dest_list: list[PrettyTransaction]

    def __bool__(self):
        return True if (self.src_list or self.dest_list) else False

    def __repr__(self):
        return f"{self.src_list}"

    def secho(self):
        for trn in self.src_list:
            trn.secho()
        for trn in self.dest_list:
            trn.secho()


@dataclass
class Signature:
    transaction_id: int
    signature: str  # store as hex
    origin: str  # src or dest
