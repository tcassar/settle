# coding=utf-8

from src.simplify.base_graph import GenericDigraph, GraphError
from src.simplify.graph_objects import Vertex
from src.simplify.specialised_graph import WeightedDigraph
import src.simplify.path as path

from dataclasses import dataclass


"""Flow Graph"""


class FlowEdgeError(Exception):
    ...


class SettleError(Exception): ...


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

    def to_dot(self):
        base = f'[label="  {self.flow}/{self.capacity}  "]'
        return base[:-1] + ", color=red]" if self.residual else base

    def unused_capacity(self):
        """Returns unused capacity of the edge"""
        return self.capacity - self.flow

    def push_flow(self, flow: int):
        """Pushes flow down an edge; raises error if too much"""
        current = self.flow
        if (new := flow + current) > self.capacity:
            print(new, self.unused_capacity())
            # raise error
            raise FlowEdgeError(
                f"Tried to add {flow} units of flow"
                f" to an edge with {self.unused_capacity()} units of flow availible, "
                f"totalling {new}/{self.capacity} units"
            )
        else:
            self.flow = new


class FlowGraph(GenericDigraph):

    def __init__(self, vertices: list[Vertex]):

        super().__init__(vertices)

        # map to keep track of people's net debts; +ve if owes group, -ve if owed by group
        self.net_debt: dict[Vertex, int] = {node: 0 for node in vertices}

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

    def add_edge(self, src: Vertex, *edges: tuple[Vertex, int], update_debt=True):
        """Add a FlowEdge to graph, and also add a residual edge"""
        for dest, capacity in edges:
            # make sure nodes in graph
            self.sanitize(src, dest)

            # add normal edge
            self[src].append(FlowEdge(dest, capacity))
            # add residual edge
            self[dest].append(FlowEdge(src, 0))

            if update_debt:
                # handle net_debt;
                self.net_debt[src] += capacity
                self.net_debt[dest] -= capacity

    def pop_edge(self, src, dest, *, update_debt=False):
        """removes REAL edges, and deletes residual counterpart"""
        # normal
        fwd_edge = self.edge_from_nodes(dest, self[src])
        self[src].remove(fwd_edge)
        # residual
        self[dest].remove(self.edge_from_nodes(src, self[dest]))

        if update_debt:
            # handle net_debt;
            self.net_debt[src] -= fwd_edge.capacity
            self.net_debt[dest] += fwd_edge.capacity

    def flow_neighbours(self, node: Vertex):
        """returns neighbours of a node including those related by residual edge
        edges are valid iff they have unused capacity"""

        # build list of edges from adj list with unused capacity
        return [edge for edge in self[node] if edge.unused_capacity()]


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
    def simplify_debt(graph: FlowGraph): ...
    people = ['tom', 'dad', 'maia']
    debt = FlowGraph([Vertex(ID, person) for ID, person in enumerate(people)])

    t, d, m = debt.nodes()

    debt.add_edge(d, (m, 5), (t, 10))
    debt.add_edge(m, (t, 5))

    debt.to_dot()



    # @staticmethod
    # def old_simplify_debt(messy: FlowGraph) -> WeightedDigraph:
    #     """Simplified debt
    #     1) Maxflow for all edges in graph
    #     2) Convert residual graph to digraph (edges with unused capacity)"""
    #
    #     # FIXME: make consistent
    #     #       Make start on B if all else fails => best graph
    #
    #     clean = WeightedDigraph(messy.nodes())
    #
    #     def show_max(src: Vertex, sink: Vertex):
    #         flow = Simplify.edmonds_karp(messy, src, sink)
    #         if flow and not messy.edge_from_nodes(sink, messy[src]).residual:
    #             clean.add_edge(src, (sink, flow))
    #
    #     queue, discovered, previous = path.Path.build_bfs_structs(messy)
    #
    #     path.Path.BFS(
    #         target=None,
    #         graph=messy,
    #         queue=queue,
    #         discovered=discovered,
    #         previous=previous,
    #         neighbours=messy.neighbours,
    #         do_to_neighbour=show_max,
    #     )
    #
    #     # check that no money has left system
    #     net_flow = sum([clean.flow_through(clean_node) for clean_node in clean.nodes()])
    #     if net_flow:
    #         raise SettleError(f"Net flow != 0, but {net_flow}")
    #
    #     messy.to_dot()