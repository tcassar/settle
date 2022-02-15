# coding=utf-8

"""
Set up graph object to be used in condensing debt settling
"""
from copy import deepcopy
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

    def __iter__(self):
        return self


class Digraph:
    """
    Simple graph; no weighting of edges, edges directional
    given no of vertices on init, edges can be added with .add_edge(src, dest)
    """

    def __init__(self, vertices: list[Vertex]) -> None:
        """
        Sets up a graph given a list of vertices
        """
        # initialise with values being empty
        # build dict checking each type as we go
        self.graph: dict[Vertex, list[Vertex]] = {
            vertex: [] if self.sanitize(vertex) else None  # type: ignore
            for vertex in vertices
        }

        self._backwards_graph = deepcopy(self.graph)

    def __str__(self):
        """Pretty print graph"""
        out = ""
        for node, adj_list in self.graph.items():
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
                raise GraphGenError(f"{test} if of type {type(test)} not Vertex ")
        return True

    def _node_in_graph(self, node: Vertex) -> bool:
        return node in self.graph

    def add_node(self, v: Vertex):
        self.graph[v] = []
        self._backwards_graph[v] = []

    def remove_node(self, v: Vertex):
        """Delete node from graph"""

        # remove edges to node being deleted by using backwards graph
        self.sanitize(v)
        pointing_to_v = self._backwards_graph[v]

        for node in pointing_to_v:
            self.graph[node].remove(v)

        self.graph.pop(v)
        self._backwards_graph.pop(v)

    def add_edge(self, src: Vertex, dest: Vertex) -> None:
        """Adds edge from src  -> destination; **directional**"""
        self.sanitize(src, dest)

        if not self._node_in_graph(src) or not self._node_in_graph(dest):
            raise GraphOpError(f"src: {src} or dest: {dest} not in graph")

        # add to graph, reverse to backwards_graph
        self.graph[src].append(dest)
        self._backwards_graph[dest].append(src)

    def remove_edge(self, src: Vertex, dest: Vertex) -> None:
        """removes dest from src's adj list"""
        self.sanitize(src, dest)

        self.graph[src].remove(dest)
        self._backwards_graph[dest].remove(src)

    def is_edge(self, src: Vertex, dest: Vertex) -> bool:
        self.sanitize(src, dest)
        return dest in self.graph[src]
