# coding=utf-8
from dataclasses import dataclass

from src.transactions.transaction import Transaction


class ConversionError(Exception):
    ...


@dataclass
class TransactionConversion:
    transactions: list[Transaction]

    def __getattr__(self, item):
        if item == "people":
            return self._gen_people()
        else:
            raise AttributeError

    def _gen_people(self) -> list[int]:
        """Generates and returns list of UIDs involved in list of transactions"""
        people = []
        for transaction in self.transactions:
            for person in [transaction.src, transaction.dest]:
                if person not in people:
                    people.append(person)

        return people

    def _gen_digraph(self): ...

