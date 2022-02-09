# coding=utf-8

"""
Set up graph object to be used in condensing debt settling
"""
from dataclasses import dataclass
from ordered_set import OrderedSet

"""
Adj list vs matrix;

Matrix only con is space complexity is O(v^2); no new nodes will be added once graph is generated
List con is edge queries are O(V) instead of O(1) like with adj. matrix
"""


class GraphGenError(Exception):
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


class BFSQueue:
    """Standard queue, but does not allow the repetition of elements; also typed as only accepting vertices"""

    # TODO: Check use of orderedset is okay

    def __init__(self):
        self.q = OrderedSet([])

    def enqueue(self, v: Vertex):
        Digraph.sanitize(v)
        _ = self.q.append(v)

    def dequeue(self):
        return self.q.pop()

    def is_empty(self) -> bool:
        return not not len(self.q)


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
        if args is not None:
            tests = [v, *args]
        else:
            tests = [v]
        for test in tests:
            if type(test) is not Vertex:
                raise GraphGenError(f"{test} if of type {type(test)} not Vertex ")
        return True

    def add_edge(self, src: Vertex, dest: Vertex) -> None:
        """Adds edge from src  -> destination; **directional**"""
        self.sanitize(src, dest)
        self.graph[src].append(dest)

    def remove_edge(self, src: Vertex, dest: Vertex) -> None:
        """removes dest from src's adj list"""
        self.sanitize(src, dest)
        self.graph[src].remove(dest)

    def is_edge(self, src: Vertex, dest: Vertex) -> bool:
        self.sanitize(src, dest)
        return dest in self.graph[src]

    def bfs(self):
        ...
