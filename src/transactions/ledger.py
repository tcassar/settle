# coding=utf-8

from src.transactions.transaction import Transaction, VerificationError
from src.crypto import keys
from src.simplify.graph_objects import Vertex
import src.simplify.flow_graph as flow

import csv
from dataclasses import dataclass, field
import os


class LedgerBuildError(Exception):
    """Error building ledger"""


@dataclass
class Ledger:
    """Multiple transactions contained to one group (assumed from building);
    built from a stream of transaction objects"""

    # ledger, big list of transactions;
    # TODO: maybe make ledger generator
    ledger: list[Transaction] = field(default_factory=lambda: [])
    nodes: list[Vertex] = field(default_factory=lambda: [])

    def __bool__(self):
        """False if ledger empty"""
        return not not self.ledger

    def append(self, transaction: Transaction) -> list[Transaction]:
        """Nice syntax for adding transactions to ledger"""

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

        for trn in self.ledger:
            trn.verify()

    def _as_flow(self):
        """Returns ledger as a flow graph"""
        # Extract IDs involved -> nodes
        nodes: set[Vertex] = set()
        for trn in self.ledger:
            nodes.add(Vertex(trn.src))
            nodes.add(Vertex(trn.dest))

        self.nodes = list(nodes)
        self.nodes.sort(key=lambda node: node.ID)

        # build flow graph with nodes
        as_flow = flow.FlowGraph(self.nodes)

        for trn in self.ledger:
            as_flow.add_edge(Vertex(trn.src), (Vertex(trn.dest), trn.amount))

        return as_flow

class LedgerLoader:
    @staticmethod
    def load_from_csv(path: str) -> list[Ledger]:
        """Load from a csv, in transaction format"""

        print('loading from csv')

        def field(str_: str) -> int:
            return header.index(str_)

        def build_trn() -> tuple[
            int, int, int, keys.RSAPublicKey, keys.RSAPublicKey, int
        ]:

            ldr = keys.RSAKeyLoaderFromNumbers()
            ldr.load(n=int(row[field("src_n")]), e=int(row[field("src_e")]))
            src_pub: keys.RSAPublicKey = keys.RSAPublicKey(ldr)

            ldr2 = keys.RSAKeyLoaderFromNumbers()
            ldr2.load(n=int(row[field("dest_n")]), e=int(row[field("dest_e")]))
            dest_pub: keys.RSAPublicKey = keys.RSAPublicKey(ldr2)

            print(src_pub, dest_pub, "---", sep='\n')

            return (
                int(row[field("src")]),
                int(row[field("dest")]),
                int(row[field("amount")]),
                src_pub,
                dest_pub,
                int(row[field("ID")]),
            )

        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found at current path: \n{os.getcwd()}")

        transactions: list[list[Transaction]] = []

        # generate transaction objects, store as list of groups of transactions
        with open(path) as csvfile:
            transaction_reader = csv.reader(csvfile, delimiter=",")
            for row in transaction_reader:
                # use header to build index of where things are
                if row[0] == "ID":
                    header: list[str] = row
                    continue

                # build transaction, keep groups intact

                trn = Transaction(*build_trn())

                try:
                    transactions[int(row[field("group")])].append(trn)

                except IndexError:
                    # make position at group if not made yet (assuming consecutive 0 indexed group numbers
                    transactions.append([trn])

        ledgers: list[Ledger] = []

        for group in transactions:
            ledgers.append(Ledger(group))

        return ledgers
