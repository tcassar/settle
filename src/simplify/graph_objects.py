# coding=utf-8

from dataclasses import dataclass


"""All objects to be used in various graphs"""


class FlowError(Exception):
    ...


@dataclass
class Vertex:
    """Representation of a vertex; carries data and ID"""

    ID: int  # IDs should be unique
    label: str = ""  # optional label

    def _key(self) -> tuple:
        """Returns immutable repr of object for hashing"""
        return self.ID, self.label

    def __str__(self):
        return self.label if self.label else str(self.ID)

    def __hash__(self):
        """for adding to lists / dicts"""
        return hash(bytes(f"{self._key()}".encode("utf8")))


@dataclass
class Edge:
    node: Vertex

    def __str__(self):
        return str(self.node)


@dataclass
class WeightedEdge(Edge):
    weight: int

    def __str__(self):
        return f"{self.node} [{self.weight}]"


@dataclass
class FlowEdge(Edge):
    capacity: int = 0
    flow: int = 0
    residual: bool = False  # class as residual edge if capacity is 0

    def __str__(self):
        return f"{self.node} [{self.flow}/{self.capacity}]"

    def unused_capacity(self) -> int:
        return self.capacity - self.flow

    def push_flow(self, flow):
        if self.flow + flow > self.capacity or type(flow) is not int:
            raise FlowError(
                f"Cannot send {flow} units down path of capacity {self.capacity}"
            )
        self.flow += flow
