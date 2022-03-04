# coding=utf-8

from src.simplify.base_graph import GenericDigraph, GraphError
from src.simplify.graph_objects import Vertex
import src.simplify.path as path

from dataclasses import dataclass


"""Flow Graph"""


class FlowEdgeError(Exception):
    ...


@dataclass(init=False)
class FlowEdge:
    def __init__(self, node: Vertex, capacity: int, flow: int = 0):
        self.node: Vertex = node  # where is edge pointing
        self.capacity: int = capacity  # non -ve;
        self.flow: int = flow  # always initialised to 0
        self.residual: bool = not capacity

    def __str__(self):
        return (
            f"{self.node} [{self.flow}/{self.capacity}], " if not self.residual else ""
        )

    def __hash__(self):
        return hash(
            f"{self.node}, {self.capacity}, {self.residual}".encode(encoding="utf8")
        )

    def to_dot(self):
        base = f'[label="  {self.flow}/{self.capacity}  "]'
        return base[:-1] + ", color=red]" if self.residual else base

    def unused_capacity(self):
        """Returns unused capacity of the edge"""
        return self.capacity - self.flow

    def push_flow(self, flow: int):
        """Pushes flow down an edge; raises error if too much"""
        current = self.flow
        if (new := current + flow) > self.unused_capacity():
            # raise error
            raise FlowEdgeError(
                f"Tried to add {flow} to an edge with {self.unused_capacity()}"
            )
        else:
            self.flow = new


class FlowGraph(GenericDigraph):
    @staticmethod
    def edge_from_nodes(node: Vertex, list_: list[FlowEdge]) -> FlowEdge:  # type: ignore
        """gets edge from a list of edges (i.e. an adjacency list) by node;
        doesn't discriminate against residual edges"""

        return GenericDigraph.edge_from_nodes(node, list_)  # type: ignore

    def get_edge(self, src: Vertex, dest: Vertex) -> FlowEdge:
        """Gets edge in graph between two nodes, residual edges included"""
        for node in [src, dest]:
            self.sanitize(node)

        return GenericDigraph.edge_from_nodes(dest, self[src])  # type: ignore

    def is_edge(self, s: Vertex, t: Vertex, *, residual=False) -> bool:
        """Checks for edge in a graph; residual = True allows broadening to include residual edges"""
        try:
            edge = self.edge_from_nodes(t, self[s])
            if residual:
                return True
            else:
                return False if edge.residual else True

        except GraphError:
            return False

    def add_edge(self, src: Vertex, dest: Vertex, capacity: int):
        """Add a FlowEdge to graph, and also add a residual edge"""
        # make sure nodes in graph
        self.sanitize(src, dest)

        # add normal edge
        self[src].append(FlowEdge(dest, capacity))
        # add residual edge
        self[dest].append(FlowEdge(src, 0))

    def pop_edge(self, src, dest):
        """removes REAL edges, and deletes residual counterpart"""
        # normal
        self[src].remove(self.edge_from_nodes(dest, self[src]))
        # residual
        self[dest].remove(self.edge_from_nodes(src, self[dest]))

    def flow_neighbours(self, node: Vertex):
        """returns neighbours of a node including those related by residual edge
        edges are valid iff they have unused capacity"""

        # build list of edges from adj list with unused capacity
        return [edge for edge in self[node] if edge.unused_capacity()]



class Simplify:
    @staticmethod
    def edmonds_karp(graph: FlowGraph) -> int:
        ...

    @staticmethod
    def augmenting_path(graph: FlowGraph, src: Vertex, sink: Vertex) -> list[Vertex]:
        # set up a bfs
        queue, discovered, previous = path.Path.build_bfs_structs(graph, src)

        return path.Path.shortest_path(
            graph, src, sink, neighbours=graph.flow_neighbours
        )

    @staticmethod
    def bottleneck(graph: FlowGraph, node_path: list[Vertex]) -> int:
        aug_path = Simplify.nodes_to_path(graph, node_path)
        remaining = [edge.unused_capacity() for edge in aug_path]
        return min(remaining)

    @staticmethod
    def augment_flow(graph: FlowGraph, node_path: list[Vertex], flow: int) -> None:
        # normal edges
        aug_path = Simplify.nodes_to_path(graph, node_path)
        for edge in aug_path:
            edge.push_flow(flow)

        # flip node path to give residual
        node_path.reverse()
        # get edges from reversed path
        res_path = Simplify.nodes_to_path(graph, node_path)

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
