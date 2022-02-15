# coding=utf-8

"""
Set up graph object to be used in condensing debt settling
"""
import copy
from collections import namedtuple
from dataclasses import dataclass

"""
Adj list vs matrix;

Matrix only con is space complexity is O(v^2); no new nodes will be added once graph is generated
List con is edge queries are O(V) instead of O(1) like with adj. matrix
"""


class GraphGenError(Exception):
    ...


class GraphOpError(Exception):
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


class BaseGraph:
    """Base basegraph that doesn't really handle edges"""

    def __init__(self, vertices: list[Vertex]) -> None:
        """
        Sets up a basegraph given a list of vertices
        """
        # initialise with values being empty
        # build dict checking each type as we go

        self.basegraph: dict[Vertex, list] = {
            vertex: [] if self.sanitize(vertex) else None  # type: ignore
            for vertex in vertices
        }

        self._backwards_graph: dict[Vertex, list[Vertex]] = copy.deepcopy(
            self.basegraph
        )

    def __str__(self):
        """Pretty print basegraph"""
        out = ""
        for node, adj_list in self.basegraph.items():
            pretty_nodes = ""
            for mapped_node in adj_list:
                pretty_nodes += f"{str(mapped_node).upper()}, "
            out += f"{str(node).upper()} -> {pretty_nodes}\n"

        return out

    @staticmethod
    def sanitize(v: Vertex, *args) -> bool:
        """Raises GraphGenError if args are not Vertex"""
        if args is not None:
            tests = [v, *args]
        else:
            tests = [v]
        for test in tests:
            if type(test) is not Vertex:
                raise GraphOpError(f"{test} if of type {type(test)} not Vertex ")

        return True

    def _node_in_graph(self, node: Vertex) -> bool:
        return node in self.basegraph

    def add_node(self, v: Vertex):
        self.basegraph[v] = []
        self._backwards_graph[v] = []

    def remove_node(self, v: Vertex):
        ...

    def is_edge(self, src: Vertex, dest: Vertex) -> bool:
        self.sanitize(src, dest)
        return dest in self.basegraph[src]  # type: ignore

    def add_edge(self, src: Vertex, dest: Vertex):
        ...

    def remove_edge(self, src: Vertex, dest: Vertex):
        """removes dest from src's adj list"""

        self.sanitize(src, dest)

        if not self._node_in_graph(src) or not self._node_in_graph(dest):
            raise GraphOpError(f"src: {src} or dest: {dest} not in graph")

        self.basegraph[src].remove(dest)
        self._backwards_graph[dest].remove(src)


class Digraph(BaseGraph):
    """
    Simple graph; no weighting of edges, edges directional
    given no of vertices on init, edges can be added with .add_edge(src, dest)
    """

    def __init__(self, vertices: list[Vertex]):
        super().__init__(vertices)
        self.graph: dict[Vertex, list[Vertex]] = self.basegraph

    def add_edge(self, src: Vertex, dest: Vertex) -> None:
        """Adds edge from src  -> destination; **directional**"""
        self.sanitize(src, dest)

        if not self._node_in_graph(src) or not self._node_in_graph(dest):
            raise GraphOpError(f"src: {src} or dest: {dest} not in graph")

        # add to graph, reverse to backwards_graph
        self.graph[src].append(dest)
        self._backwards_graph[dest].append(src)

    def remove_node(self, v: Vertex):
        """Delete node from basegraph"""

        # remove edges to node being deleted by using backwards graph
        self.sanitize(v)
        pointing_to_v = self._backwards_graph[v]

        for node in pointing_to_v:
            if self._node_in_graph(v):
                self.basegraph[node].remove(v)
            else:
                raise GraphGenError(f"Node {v} not in graph")

        self.basegraph.pop(v)
        self._backwards_graph.pop(v)


class WeightedDigraph(BaseGraph):
    def __init__(self, vertices: list[Vertex]):
        """Build nodes for weighted digraph"""

        super().__init__(vertices)

        Edge = namedtuple("Edge", "node weight")  # type: ignore
        self.graph: dict[Vertex, list[Edge]] = self.basegraph

        self.Edge = Edge

    def __str__(self):
        """Pretty print basegraph"""
        out = ""
        for node, adj_list in self.graph.items():
            pretty_nodes = ""
            for mapped_node in adj_list:
                pretty_nodes += f"{mapped_node.node}[{mapped_node.weight}], "
            out += f"{str(node).upper()} -> {pretty_nodes}\n"

        return out

    # noinspection PyMethodOverriding
    def add_edge(self, src: Vertex, dest: Vertex, weight: int):  # type: ignore
        """Adds a weighted edge"""

        # sanitize and raise errors if input not acceptable
        self.sanitize(src, dest)
        if type(weight) is not int:
            raise GraphGenError(
                f"Weights need to be integers, not {weight} which is {type(weight)} "
            )

        # make sure nodes are present in graph
        if not self._node_in_graph(src) or not self._node_in_graph(dest):
            raise GraphOpError(f"src: {src} or dest: {dest} not in graph")

        # build edge, append to graphs
        self.graph[src].append(self.Edge(dest, weight))
        self._backwards_graph[dest].append(src)

    def remove_node(self, v: Vertex):
        self.sanitize(v)
        if v not in self.graph:
            raise GraphOpError

        pointing_to_v: list[Vertex] = self._backwards_graph[v]

        for node in pointing_to_v:
            for edge in self.graph[node]:
                if edge.node == v:
                    self.graph[node].remove(edge)
