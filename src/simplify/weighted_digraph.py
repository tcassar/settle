# coding=utf-8

from src.simplify.base_graph import GenericDigraph, GraphError
from src.simplify.graph_objects import Vertex, WeightedEdge


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
