# coding=utf-8
import copy

import settling.graph_objects
import settling.specialised_graph
from settling.specialised_graph import FlowGraph, WeightedDigraph
from settling.path import Path


class Flow:
    """Namespace for all flow operations"""

    @staticmethod
    def edmonds_karp(
        graph: FlowGraph, source: settling.graph_objects.Vertex, sink: settling.graph_objects.Vertex
    ) -> int:
        max_flow = 0

        while aug_path := Flow.find_aug_path(graph, source, sink):
            # get path's bottleneck, add to max flow
            bottleneck = graph.bottleneck(aug_path)
            max_flow += bottleneck

            # augment path
            Flow.augment_path(graph, aug_path, bottleneck)

        return max_flow

    @staticmethod
    def find_aug_path(
        graph: FlowGraph, u: settling.graph_objects.Vertex, v: settling.graph_objects.Vertex
    ) -> list[settling.graph_objects.Vertex]:
        return Path.shortest_path(graph, u, v, graph.flow_neighbours)

    @staticmethod
    def augment_path(graph: FlowGraph, path: list[settling.graph_objects.Vertex], bottleneck: int):
        """Push flow down path, push flow up residual paths"""
        residual_path = copy.deepcopy(path)
        residual_path.reverse()

        graph.push_flow(path, bottleneck)
        graph.push_flow(residual_path, bottleneck * -1)

    @staticmethod
    def simplify_debt(messy):
        def cleanup(current: settling.graph_objects.Vertex, neighbour: settling.graph_objects.Vertex) -> None:
            """To be passed into bfs
            calculates max flow from current -> neighbour, adds edge to clean with that weight"""

            if flow := Flow.edmonds_karp(messy, current, neighbour):
                # add max flow edge to clean graph
                clean.add_edge(current, (neighbour, flow))
                # pop edge from messy
                messy.pop_edge(current, neighbour)

        # create clean graph with no edges
        clean = settling.specialised_graph.WeightedDigraph(messy.nodes())

        for src, edge_list in messy.graph.items():
            for edge in edge_list:
                cleanup(src, edge.node)

        return clean

    @staticmethod
    def di_to_flow(digraph: WeightedDigraph) -> FlowGraph:
        """Converts a weighted digraph to a flow graph with 0 flow along each edge"""

        flow = FlowGraph(digraph.nodes())

        for src, edge_list in digraph.graph.items():
            for edge in edge_list:
                flow.add_edge(src, (edge.node, edge.weight))  # type: ignore

        return flow