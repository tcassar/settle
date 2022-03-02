import copy
import logging

import settling.graph_objects
import settling.specialised_graph
from settling import base_graph as graphs
from settling.specialised_graph import FlowGraph
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

        logging.debug(f"{max_flow} units from {source} -> {sink}")
        return max_flow

    @staticmethod
    def find_aug_path(
        graph: FlowGraph, u: settling.graph_objects.Vertex, v: settling.graph_objects.Vertex
    ) -> list[settling.graph_objects.Vertex]:
        logging.debug(f"Found augmenting path from {u} -> {v}")
        return Path.shortest_path(graph, u, v, graph.flow_neighbours)

    @staticmethod
    def augment_path(graph: FlowGraph, path: list[settling.graph_objects.Vertex], bottleneck: int):
        """Push flow down path, push flow up residual paths"""
        residual_path = copy.deepcopy(path)
        residual_path.reverse()

        graph.push_flow(path, bottleneck)
        graph.push_flow(residual_path, bottleneck * -1)
        logging.debug(f"Augmented path {path} by {bottleneck}")

    @staticmethod
    def simplify_debt(messy: settling.specialised_graph.FlowGraph) -> settling.specialised_graph.WeightedDigraph:
        """One round of graph simplification; done by walking through graph w/ BFS,
        applying maxflow to every neighbour in graph"""

        # FIXME: Make consistent for all starting points

        logging.debug(f"cleaning {messy}")

        def get_max(src: settling.graph_objects.Vertex, sink: settling.graph_objects.Vertex) -> int:
            """Helper to improve readability. Gets max flow between src and sink"""
            return Flow.edmonds_karp(messy, src, sink)

        def cleanup(current: settling.graph_objects.Vertex, neighbour: settling.graph_objects.Vertex) -> None:
            """To be passed into bfs
            calculates max flow from current -> neighbour, adds edge to clean with that weight"""

            if flow := get_max(current, neighbour):
                # add max flow edge to clean graph
                clean.add_edge(current, (neighbour, flow))
                # pop edge from messy
                messy.pop_edge(current, neighbour)

        # create clean graph with no edges
        clean = settling.specialised_graph.WeightedDigraph(messy.nodes())

        # build queue, discovered hash map and prev hash maps
        queue, discovered, previous = Path.build_bfs_structs(messy)
        logging.debug(f"Queue: {queue}\nDiscovered: {discovered}\nPrevious: {previous}")

        logging.debug("starting walk")

        Path.BFS(
            graph=messy,
            queue=queue,
            discovered=discovered,
            target=None,
            previous=previous,
            do_to_neighbour=cleanup,
            neighbours=messy.neighbours,
        )

        return clean
