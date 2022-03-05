# coding=utf-8

"""
Set up graph object to be used in condensing debt settling
"""
import copy

import graphviz

from src.simplify.graph_objects import Vertex, Edge


class GraphError(Exception):
    ...


class Default:
    def __gt__(self, other):
        return True


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
                pretty_nodes += f"{str(edge).upper()}"
            out += f"{str(node).upper()} -> {pretty_nodes}\n"

        return out

    def __len__(self):
        return len(self.graph)

    def __getitem__(self, item):
        return self.graph[item]

    def __eq__(self, other):
        return self.graph == other

    def to_dot(self, *, n: int = 0, title="graph"):
        """prints dot representation of graph"""
        dot_source = ''
        for src, adj_list in self.graph.items():
            for edge in adj_list:
                dot_source += f"{str(src)} -> {str(edge.node)} {edge.to_dot()}\n"
            if not adj_list:
                dot_source += f"{src}\n"

        dot = graphviz.Source(f"digraph {{ {dot_source} }}")
        dot.format = "svg"
        dot.render(f"./graph_renders/{title}{n}")

    def nodes(self) -> list[Vertex]:
        """Returns nodes in the graph"""
        return list(self.graph.keys())

    @staticmethod
    def edge_from_nodes(node: Vertex, list_: list[Edge]) -> Edge:
        """Checks if node is in a list of edges, will return relevant edge if found
        usage:"""
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

    def is_node(self, v: Vertex) -> bool:
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

    def is_edge(self, s: Vertex, t: Vertex) -> int:
        """Checks for an edge between nodes (directional: s->t !=> t->s)"""
        try:
            self.edge_from_nodes(t, self.graph[s])
            return 1
        except GraphError:
            return 0

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
