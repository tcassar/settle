# coding=utf-8

from src.simplify.flow_algorithms import Simplify, SettleError
import src.simplify.flow_graph as flow
from src.crypto import keys
from src.simplify.graph_objects import Vertex
from src.transactions.transaction import Transaction, VerificationError

import csv
import os
from dataclasses import dataclass, field


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
    key_map: dict[int, keys.RSAPublicKey] = field(default_factory=lambda: {})

    def __bool__(self):
        """False if ledger empty"""
        return not not self.ledger

    def __eq__(self, other):
        return self.ledger == other.ledger

    def append(self, transaction: Transaction) -> list[Transaction]:
        """Nice syntax for adding transactions to ledger"""

        if type(transaction) is not Transaction:
            raise LedgerBuildError(
                f"cannot append type {transaction} to ledger; must be transaction"
            )
        else:
            self.ledger.append(transaction)
            self.key_map[transaction.src] = transaction.src_pub
            self.key_map[transaction.dest] = transaction.dest_pub

        return self.ledger

    def _verify_transactions(self) -> None:
        """Verifies the keys of all the transactions in the group.
        Raises error if a faulty transaction is found"""

        for trn in self.ledger:
            trn.verify()

    def _as_flow(self) -> flow.FlowGraph:
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

        # verify transaction, add to graph
        for trn in self.ledger:
            trn.verify()
            as_flow.add_edge(Vertex(trn.src), (Vertex(trn.dest), trn.amount))

        return as_flow

    def _flow_to_transactions(self, fg: flow.FlowGraph) -> list[Transaction]:
        """For each edge, make a transaction"""

        new_trns: list[Transaction] = []

        edge: flow.FlowEdge

        # go through every outgoing transaction by person
        for person, adj_list in fg.graph.items():
            for edge in adj_list:  # type: ignore

                # don't add residual edges to ledger
                if edge.residual:
                    continue

                else:
                    # generate UNSIGNED transactions
                    # TODO: let db handle id; keep it initialised to 0
                    edge: flow.FlowEdge  # type: ignore
                    trn = Transaction(
                        edge.src.ID,
                        edge.node.ID,
                        edge.capacity,
                        self.key_map[edge.src.ID],
                        self.key_map[edge.node.ID],
                    )

                    new_trns.append(trn)

        return new_trns

    def simplify_ledger(self):
        # build ledger as a flow graph
        fg = self._as_flow()
        fg.to_dot(title='pre_settle')
        try:
            simplified_fg = Simplify.simplify_debt(fg)

            # settle, update ledger
            simplified_fg.to_dot(title='settled')
            self.ledger = self._flow_to_transactions(simplified_fg)

        except SettleError:
            # no changes made to graph, keep ledger as is, with sigs.
            print('Graph already at few transactions per person; no optimisations found')

        except VerificationError as ve:
            # let verification error propagate up
            raise ve


class LedgerLoader:
    @staticmethod
    def load_from_csv(path: str) -> list[Ledger]:
        """Load from a csv, in transaction format"""

        print("loading from csv")

        def get_field(str_: str) -> int:
            return header.index(str_)

        def build_trn() -> tuple[
            int, int, int, keys.RSAPublicKey, keys.RSAPublicKey, int
        ]:

            ldr = keys.RSAKeyLoaderFromNumbers()
            ldr.load(n=int(row[get_field("src_n")]), e=int(row[get_field("src_e")]))  # type: ignore
            src_pub: keys.RSAPublicKey = keys.RSAPublicKey(ldr)

            ldr2 = keys.RSAKeyLoaderFromNumbers()
            ldr2.load(n=int(row[get_field("dest_n")]), e=int(row[get_field("dest_e")]))  # type: ignore
            dest_pub: keys.RSAPublicKey = keys.RSAPublicKey(ldr2)

            print(src_pub, dest_pub, "---", sep="\n")

            return (
                int(row[get_field("src")]),
                int(row[get_field("dest")]),
                int(row[get_field("amount")]),
                src_pub,
                dest_pub,
                int(row[get_field("ID")]),
            )

        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found at current path: \n{os.getcwd()};\nsearched for {path}")

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
                    transactions[int(row[get_field("group")])].append(trn)

                except IndexError:
                    # make position at group if not made yet (assuming consecutive 0 indexed group numbers
                    transactions.append([trn])

        ledgers: list[Ledger] = []

        for group in transactions:
            ledger = Ledger()
            for trn in group:
                ledger.append(trn)
            ledgers.append(ledger)

        return ledgers
