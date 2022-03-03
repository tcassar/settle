# coding=utf-8

import src.simplify.graph_objects as graph_objects
from src.simplify.path import Path
from src.simplify.specialised_graph import FlowGraph, WeightedDigraph

import copy


class Flow:
    """Namespace for all flow operations"""

    @staticmethod
    def edmonds_karp(
        graph: FlowGraph,
        source: graph_objects.Vertex,
        sink: graph_objects.Vertex,
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
        graph: FlowGraph,
        u: graph_objects.Vertex,
        v: graph_objects.Vertex,
    ) -> list[graph_objects.Vertex]:
        return Path.shortest_path(graph, u, v, graph.flow_neighbours)

    @staticmethod
    def augment_path(
        graph: FlowGraph, path: list[graph_objects.Vertex], bottleneck: int
    ):
        """Push flow down path, push flow up residual paths"""
        residual_path = copy.deepcopy(path)
        residual_path.reverse()

        graph.push_flow(path, bottleneck)
        graph.push_flow(residual_path, bottleneck * -1)

    # @staticmethod
    # def simplify_debt(messy):
    #     def cleanup(
    #         current: graph_objects.Vertex,
    #         neighbour: graph_objects.Vertex,
    #     ) -> None:
    #         """To be passed into bfs
    #         calculates max flow from current -> neighbour, adds edge to clean with that weight"""
    #
    #         if flow := Flow.edmonds_karp(messy, current, neighbour):
    #             # add max flow edge to clean graph
    #             clean.add_edge(current, (neighbour, flow))
    #             # pop edge from messy
    #             messy.pop_edge(current, neighbour)
    #
    #     # create clean graph with no edges
    #     clean = WeightedDigraph(messy.nodes())
    #
    #     for src, edge_list in messy.graph.items():
    #         for edge in edge_list:
    #             cleanup(src, edge.node)
    #
    #     return clean

    @staticmethod
    def simplify_debt(messy: FlowGraph) -> WeightedDigraph:
        """Simplified debt
        1) Maxflow for all edges in graph
        2) Convert residual graph to digraph (edges with unused capacity)"""

        # initialise infrastructure for search through graph
        queue, discovered, previous = Path.build_bfs_structs(messy)

        def max_flow(current: graph_objects.Vertex, neighbour: graph_objects.Vertex):
            # messy.pop_edge(current, neighbour)
            return Flow.edmonds_karp(messy, current, neighbour)


        # search with no target (thus hitting all edges) with bfs, maxflowing each
        Path.BFS(
            target=None,
            graph=messy,
            queue=queue,
            discovered=discovered,
            previous=previous,
            neighbours=messy.neighbours,
            do_to_neighbour=max_flow,
        )

        print(messy)

        return messy
