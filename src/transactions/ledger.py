# coding=utf-8
from typing import Tuple

from src.transactions.transaction import Transaction

import csv
from dataclasses import dataclass, field
import os


class LedgerLoader:

    @staticmethod
    def load_from_csv(path: str) -> list[list[Transaction]]:
        """Load from a csv, in transaction format"""

        def field(str_: str) -> int:
            return header.index(str_)

        def build_trn() -> tuple[str, str, int, int]:
            return row[field('src')], row[field('dest')], int(row[field('amount')]), int(row[field('ID')])

        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found at current path: \n{os.getcwd()}")

        transactions: list[list[Transaction]] = []

        with open(path) as csvfile:
            transaction_reader = csv.reader(csvfile, delimiter=',')
            for row in transaction_reader:
                # use header to build index of where things are
                if row[0] == 'ID':
                    header: list[str] = row
                    continue

                # build transaction, keep groups intact
                try:
                    transactions[field('group')].append(Transaction(*build_trn()))
                except IndexError:
                    # posn at group not made yet
                    transactions.append([Transaction(*build_trn())])


        return transactions



@dataclass
class Ledger:
    """Multiple transactions contained to one group (assumed from building);
    built from a stream of transaction objects"""

    # ledger, big list of transactions;
    # TODO: maybe make ledger generator
    ledger: list[Transaction] = field(default_factory=lambda: [])

    def __bool__(self):
        """False if ledger empty"""
        return not not self.ledger

    def append(self, transaction: Transaction) -> list[Transaction]:
        """Nice syntax for adding transactions to ledger"""
        print(type(transaction))

        if type(transaction) is not Transaction:
            raise LedgerBuildError(
                f"cannot append type {transaction} to ledger; must be transaction"
            )
        else:
            self.ledger.append(transaction)

        return self.ledger

    def _verify_transactions(self):
        """Verifies the keys of all the transactions in the group.
        Raises error if a faulty transaction is found"""


class LedgerBuildError(Exception):
    """Error building ledger"""