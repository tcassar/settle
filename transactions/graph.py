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


class FlowError(Exception):
    ...


class Default:
    def __gt__(self, other):
        return True


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
    residual: bool = not capacity  # class as residual edge if capacity is 0

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
                pretty_nodes += f"{str(edge).upper()}, "
            out += f"{str(node).upper()} -> {pretty_nodes}\n"

        return out

    def __len__(self):
        return len(self.graph)

    def __getitem__(self, item):
        return self.graph[item]

    def __eq__(self, other):
        return self.graph == other

    def nodes(self) -> list[Vertex]:
        """Returns nodes in the graph"""
        return list(self.graph.keys())

    @staticmethod
    def edge_from_nodes(node: Vertex, list_: list[Edge]) -> Edge:
        """Checks if node is in a list of edges, will return relevant edge if found"""
        for edge in list_:
            if edge.node == node:
                return edge
            else:
                continue

        raise GraphError("Node not in list")

    @staticmethod
    def nodes_from_edges(edges: list[Edge]) -> list[Vertex]:
        nodes = []
        for edge in edges:
            nodes.append(edge.node)
        return nodes

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
        # look at _backwards_graph to find associations
        for edge in self._backwards_graph[v]:
            # removing B from A and C; A's pass
            pointing_node_neighbours = self._backwards_graph[
                edge.node
            ]  # [Edge(A), Edge(C)]
            pointing_edge = self.edge_from_nodes(v, self.graph[edge.node])
            self.graph[edge.node].remove(pointing_edge)  # type: ignore

        return {v: self.graph.pop(v)}

    def is_edge(self, s: Vertex, t: Vertex) -> bool:
        """Checks for an edge between nodes (directional: s->t !=> t->s"""
        try:
            return not not self.edge_from_nodes(t, self.graph[s])
        except GraphError:
            return False

    def pop_edge(self, s: Vertex, t: Vertex) -> Edge:
        self.sanitize(s, t)
        edge = self.edge_from_nodes(t, self.graph[s])

        if edge is None:
            raise GraphError("Cannot pop edge that doesnt exist")

        self.graph[s].remove(edge)
        return edge

    def neighbours(self, node: Vertex) -> list[Edge]:
        self.sanitize(node)
        return self[node]

    def connected(self, node: Vertex) -> bool:
        """Returns true if node has connections to graph"""
        forwards = self[node]
        backwards = self._backwards_graph[node]
        return True if forwards or backwards else False


class Digraph(GenericDigraph):
    def add_edge(self, s: Vertex, *args: Vertex) -> None:
        self.sanitize(s, *args)
        for target in args:
            self.graph[s].append(Edge(target))
            self._backwards_graph[target].append(Edge(s))


class WeightedDigraph(GenericDigraph):
    def add_edge(self, source: Vertex, *edges: tuple[Vertex, int]) -> None:
        # sanitize source
        self.sanitize(source)

        for node, weight in edges:
            self.sanitize(node)
            self.graph[source].append(WeightedEdge(node, weight))
            self._backwards_graph[node].append(WeightedEdge(source, weight * -1))


class FlowGraph(WeightedDigraph):
    """
    Flow Graph
    Keeps a residual graph
    Can be operated on by BFS
    Can have max flow found
    Uses Max Flow edges

    Assumes no two way edges: may be problematic
    """

    @staticmethod
    def edge_from_nodes(node: Vertex, list_: list[Edge]) -> FlowEdge:
        return Digraph.edge_from_nodes(node, list_)  # type: ignore

    def add_edge(self, source: Vertex, *edges: tuple[Vertex, int]) -> None:
        # sanitize source
        self.sanitize(source)

        for node, capacity in edges:
            self.sanitize(node)

            # add normal edges
            self.graph[source].append(FlowEdge(node, capacity))
            self._backwards_graph[node].append(FlowEdge(source, capacity * -1))

            # add residual edges
            self.graph[node].append(FlowEdge(source, 0))

    def pop_edge(self, s: Vertex, t: Vertex) -> Edge:
        # pop residual edge as well

        edge = self.edge_from_nodes(s, self.graph[t])

        if edge is None:
            raise GraphError("Cannot pop edge that doesn't exist")

        self.graph[t].remove(edge)
        return super().pop_edge(s, t)

    def flow_neighbours(self, node: Vertex) -> list[Edge]:
        """Only returns valid neighbours for maxflow (i.e. residual edges included, only where capacity > 0"""
        filtered: list[FlowEdge] = []
        # FlowEdge can be treated as Edge, Edge cannot be treated as flow edge (*)
        unfiltered: list[FlowEdge] = self[node]  # type: ignore
        for edge in unfiltered:
            if edge.unused_capacity():
                filtered.append(edge)

        # fine as (*)
        return filtered  # type: ignore

    def push_flow(self, path: list[Vertex], flow: int):
        """Pushes flow along path; path denoted as [Vertex(A), Vertex(B)... Vertex(X)]
        1) get neighbouring edges of first person in path
        2) push flow along A -> B
        3) iterate for len(list) - 1
        """

        for node, next_ in zip(path, path[1:]):
            flow_edge: FlowEdge = self.edge_from_nodes(next_, self[node])  # type: ignore
            flow_edge.push_flow(flow)

    def bottleneck(self, path: list[Vertex]) -> int:
        """Returns the bottleneck (the lowest remaining capacity of an edge) along a path"""
        bottleneck: Default | int = Default()
        for node, next_ in zip(path, path[1:]):
            edge = self.edge_from_nodes(next_, self.graph[node])
            if (flow := edge.unused_capacity()) < bottleneck:
                bottleneck = flow

        if type(bottleneck) == Default:
            bottleneck = 0

        return bottleneck  # type: ignore
