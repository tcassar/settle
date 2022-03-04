# coding=utf-8
from typing import Tuple

from src.simplify.base_graph import GenericDigraph, Digraph, GraphError, Default
from src.simplify.graph_objects import Vertex, WeightedEdge, Edge, FlowEdge


class WeightedDigraph(GenericDigraph):
    def add_edge(self, source: Vertex, *edges: tuple[Vertex, int]) -> None:

        # sanitize source
        self.sanitize(source)
        for node, weight in edges:
            if self.is_edge(source, node):
                existing: WeightedEdge
                existing = self.edge_from_nodes(node, self[source])  # type: ignore
                existing.weight += weight
            else:
                self.sanitize(node)
                self.graph[source].append(WeightedEdge(node, weight))
                self._backwards_graph[node].append(WeightedEdge(source, weight * -1))

    def flow_through(self, node: Vertex) -> int:
        """Returns sum of weights out of node
        +ve => net flow out of node
        -ve => net flow into node"""
        flow = 0
        edge: WeightedEdge

        for graph in [self.graph, self._backwards_graph]:
            for edge in graph[node]:  # type: ignore
                flow += edge.weight

        # return -ve, as backwards edges have -ve value and forwards have +ve
        return flow

    def net_debts(self) -> dict[Vertex, int]:
        """Returns a map of everyone with net money owed (-ve if they need to pay)"""
        return {node: self.flow_through(node) for node in self.nodes()}

    def is_edge(self, s: Vertex, t: Vertex) -> int:
        try:
            edge: WeightedEdge
            edge = self.edge_from_nodes(t, self.graph[s])  # type: ignore
            return edge.weight
        except GraphError:
            return 0


class FlowGraph(WeightedDigraph):
    """
    Flow Graph
    Keeps a residual graph
    Can be operated on by BFS
    Can have max flow found
    Uses Max Flow edges

    For write up, talk about improving with a round of cycle detection
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
            self.graph[node].append(FlowEdge(source, 0, residual=True))

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

    def flow_through(self, node: Vertex) -> int:
        """Returns current flow through node
        +ve direction out of node => give us net money one owes to group
        """
        flow = 0
        edge: FlowEdge

        for graph, name in zip(
            [self.graph, self._backwards_graph], ["forward", "backwards"]
        ):
            for edge in graph[node]:  # type: ignore
                flow += edge.flow

        return flow

    def is_edge(self, s: Vertex, t: Vertex) -> int:
        try:
            edge: FlowEdge
            edge = self.edge_from_nodes(t, self.graph[s])  # type: ignore
            return edge.flow
        except GraphError:
            return 0
