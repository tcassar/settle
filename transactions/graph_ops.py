# coding=utf-8

import transactions.graph as graphs


class GraphOps:
    """Namespace for graph operations"""

    @staticmethod
    def is_path(
        graph: graphs.GenericDigraph, source: graphs.Vertex, sink: graphs.Vertex
    ) -> list[graphs.Edge]:
        """Uses a recursive implementation of BFS to find path between nodes"""
