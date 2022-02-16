# coding=utf-8

"""
Set up graph object to be used in condensing debt settling
"""
import copy
from dataclasses import dataclass

"""
Adj list vs matrix;

Matrix only con is space complexity is O(v^2); no new nodes will be added once graph is generated
List con is edge queries are O(V) instead of O(1) like with adj. matrix
"""


class GraphError(Exception):
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
        return self.label

    def __hash__(self):
        """for adding to lists / dicts"""
        return hash(bytes(f"{self._key()}".encode("utf8")))


@dataclass
class Edge:
    node: Vertex


@dataclass
class WeightedEdge(Edge):
    weight: int


class GenericDigraph:
    def __init__(self, vertices: list[Vertex]) -> None:
        """
        Sets up a graph given a list of vertices
        """
        # initialise with values being empty
        # build dict checking each type as we go

        self.graph: dict[Vertex, list[Edge]] = {
            vertex: [] if self.sanitize(vertex) else None  # type: ignore
            for vertex in vertices
        }

        self._backwards_graph: dict[Vertex, list[Edge]] = copy.deepcopy(self.graph)

    def __str__(self):
        """Pretty print graph"""
        out = ""
        for node, adj_list in self.graph.items():
            pretty_nodes = ""
            for edge in adj_list:
                pretty_nodes += f"{str(edge.node).upper()}"
                if type(edge) == WeightedEdge:
                    pretty_nodes += f"[{edge.weight}]"  # type: ignore
                pretty_nodes += ", "
            out += f"{str(node).upper()} -> {pretty_nodes}\n"

        return out

    @staticmethod
    def node_in_list(node: Vertex, list_: list[Edge]) -> Edge | None:
        """Checks if node is in a list of edges, will return relevant edge if found"""
        for edge in list_:
            if edge.node == node:
                return edge
            else:
                continue

        return None

    @staticmethod
    def sanitize(v: Vertex, *args) -> bool:
        """Raises GraphGenError if args are not Vertex"""
        if args is not None:
            tests = [v, *args]
        else:
            tests = [v]
        for test in tests:
            if type(test) is not Vertex:
                raise GraphError(f"{test} if of type {type(test)} not Vertex ")

        return True

    def is_node(self, v: Vertex):
        return v in self.graph

    def add_node(self, v: Vertex) -> None:
        self.graph[v] = []
        self._backwards_graph[v] = []

    def pop_node(self, v: Vertex) -> dict[Vertex, list[Edge]]:
        """Pops node, returns key/value pair of node and previous connections"""
        return {v: self.graph.pop(v)}

    def is_edge(self, s: Vertex, t: Vertex) -> bool:
        """Checks for an edge between nodes (directional: s->t !=> t->s"""
        return True if self.node_in_list(t, self.graph[s]) is not None else False

    def pop_edge(self, s: Vertex, t: Vertex) -> Edge:
        self.sanitize(s, t)
        edge = self.node_in_list(t, self.graph[s])

        if edge is None:
            assert edge is not None
            raise GraphError("Cannot pop edge that doesnt exist")

        self.graph[s].remove(edge)
        return edge


class Digraph(GenericDigraph):
    def add_edge(self, s: Vertex, t: Vertex) -> None:
        self.sanitize(s, t)
        self.graph[s].append(Edge(t))


class WeightedDigraph(GenericDigraph):
    def add_edge(self, s: Vertex, t: Vertex, weight: int) -> None:
        self.sanitize(s, t)
        self.graph[s].append(WeightedEdge(t, weight))
