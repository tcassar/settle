import copy

from simplify import path as path
from simplify.flow_graph import FlowGraph, FlowEdge
from simplify.graph_objects import Vertex


class SettleError(Exception):
    ...


class NoOptimisations(Exception):
    """No optimisations to graph; already in simplest form"""


class MaxFlow:
    @staticmethod
    def edmonds_karp(graph: FlowGraph, src: Vertex, sink: Vertex) -> int:

        max_flow = 0

        while aug_path := MaxFlow.augmenting_path(graph, src, sink):
            bottleneck = MaxFlow.bottleneck(graph, aug_path)
            max_flow += bottleneck

            MaxFlow.augment_flow(graph, aug_path, bottleneck)
            # graph.to_dot()

        return max_flow

    @staticmethod
    def augmenting_path(graph: FlowGraph, src: Vertex, sink: Vertex) -> list[Vertex]:
        """find the shortest path from src -> sink using BFS"""
        return path.Path.shortest_path(
            graph, src, sink, neighbours=graph.flow_neighbours
        )

    @staticmethod
    def bottleneck(graph: FlowGraph, node_path: list[Vertex]) -> int:
        """Returns bottleneck of a path"""
        aug_path = MaxFlow.nodes_to_path(graph, node_path)
        remaining = [edge.unused_capacity() for edge in aug_path]
        return min(remaining)

    @staticmethod
    def augment_flow(graph: FlowGraph, node_path: list[Vertex], flow: int) -> None:
        """Adds flow to normal edges of path, subtracts from residual
        deals with pushing to residual and hence subtracting from normal"""
        # normal edges
        aug_path = MaxFlow.nodes_to_path(graph, node_path)
        for edge in aug_path:
            edge.push_flow(flow)

        # flip node path to give residual
        node_path.reverse()
        # get edges from reversed path
        res_path = MaxFlow.nodes_to_path(graph, node_path)

        # push flow down res path
        for edge in res_path:
            edge.push_flow(flow * -1)

    @staticmethod
    def nodes_to_path(graph: FlowGraph, nodes: list[Vertex]) -> list[FlowEdge]:
        graph.sanitize(*nodes)

        edges: list[FlowEdge] = []
        for src, neighbour in zip(nodes, nodes[1:]):
            edges.append(graph.get_edge(src, neighbour))

        return edges


class Simplify:
    @staticmethod
    def simplify_debt(debt: FlowGraph) -> FlowGraph:
        """
        for edge(u, v) in graph:
            if new := maxflow(u, v):
                clean.add_edge(u, (v, new))
                messy.adjust_edges()
        """

        clean = FlowGraph(debt.nodes())

        d_cache = copy.deepcopy(debt)

        # TODO: optimise for starting with nodes with least incoming edges

        # iterate through edges in graph:
        while not not debt:
            edge: FlowEdge  # type: ignore
            for (node, adj_list) in debt.graph.items():

                for edge in adj_list:  # type: ignore
                    if not edge.residual:
                        if flow := MaxFlow.edmonds_karp(debt, node, edge.node):
                            clean.add_edge(node, (edge.node, flow))
                        debt.adjust_edges()

        if clean == d_cache:
            clean.to_dot(n=1)
            raise NoOptimisations

        if d_cache.net_debt != clean.net_debt:
            raise SettleError("Settling failed; debt was skewed")

        return clean