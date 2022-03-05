# coding=utf-8

from dataclasses import dataclass

import src.simplify.specialised_graph as graphs

from src.simplify.graph_objects import *
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

    def _gen_digraph(self):

        # build list of vertices
        def id_to_vertex(id: int) -> Vertex:
            return Vertex(ID=id)

        digraph = graphs.WeightedDigraph(list(map(id_to_vertex, self._gen_people())))
        print(digraph)
