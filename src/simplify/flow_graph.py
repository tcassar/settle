# coding=utf-8
from dataclasses import dataclass

from src.simplify.base_graph import GenericDigraph, GraphError
from src.simplify.graph_objects import Vertex

"""Flow Graph"""


class FlowEdgeError(Exception):
    ...


class EdgeCapacityZero(Exception):
    ...


@dataclass(init=False, repr=False, eq=False)
class FlowEdge:
    def __init__(self, src: Vertex, node: Vertex, capacity: int, flow: int = 0):
        self.src: Vertex = src
        self.node: Vertex = node  # where is edge pointing
        self.capacity: int = capacity  # non -ve;
        self.flow: int = flow  # always initialised to 0
        self.residual: bool = not capacity

    def __str__(self):
        return (
            f"{self.node} [{self.flow}/{self.capacity}], "
            if not self.residual
            else f"R: {self.node} [{self.flow}/{self.capacity}],"
        )

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        # TODO: write this properly
        return str(self) == str(other)

    def __lt__(self, other):
        return self.capacity < other.capacity

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
                f" to an edge with {self.unused_capacity()} units of flow available, "
                f"totalling {new}/{self.capacity} units"
            )
        else:
            self.flow = new

    def adjust_edge(self):
        """Changes edge values so that capacity = unused_capacity, flow = 0"""
        if self.residual:
            # reset residual edge
            self.flow = 0

        else:
            # make capacity = to what was unused capacity, unless unused capacity 0;
            # if unused capacity 0, raise EdgeCapacityZero
            if new := self.unused_capacity():
                self.capacity = new
                self.flow = 0
            else:
                raise EdgeCapacityZero(self, new)


class FlowGraph(GenericDigraph):
    def __init__(self, vertices: list[Vertex]):

        super().__init__(vertices)

        # map to keep track of people's net debts; +ve if owes group, -ve if owed by group
        self.net_debt: dict[Vertex, int] = {node: 0 for node in vertices}

    def __bool__(self):
        """Returns true if not empty"""
        return not ({node: [] for node in self.nodes()} == self.graph)

    def __eq__(self, other):
        return str(self) == str(other)

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
            self[src].append(FlowEdge(src, dest, capacity))
            # add residual edge
            self[dest].append(FlowEdge(dest, src, 0))

            self[src].sort(reverse=True)

            if update_debt:
                # handle net_debt;
                self.net_debt[src] += capacity
                self.net_debt[dest] -= capacity

    def pop_edge(self, src: Vertex, dest: Vertex, *, update_debt=False):
        """removes REAL edges, and deletes residual counterpart"""

        # normal
        fwd_edge = self.edge_from_nodes(dest, self[src])
        self[src].remove(fwd_edge)
        # residual
        res = self.edge_from_nodes(src, self[dest])
        if res.node == src:
            # assert self[dest][0] == self[dest][1]
            self[dest].remove(res)

        else:
            raise ValueError(
                f"Tried to pop residual edge; intended {dest} -> {src}, got {dest} -> {res.node}"
            )

        if update_debt:
            # handle net_debt;
            self.net_debt[src] -= fwd_edge.capacity
            self.net_debt[dest] += fwd_edge.capacity

    def flow_neighbours(self, node: Vertex):
        """returns neighbours of a node including those related by residual edge
        edges are valid iff they have unused capacity"""

        # build list of edges from adj list with unused capacity
        return [edge for edge in self[node] if edge.unused_capacity()]

    def adjust_edges(self):
        """Run edge adjust on each edge, if new capacity = 0 and residual = false,
        delete ede + residual counterpart"""

        edge: FlowEdge

        for n, node in enumerate(self.nodes()):
            for edge in self[node]:
                try:
                    edge.adjust_edge()
                except EdgeCapacityZero:
                    # edge no longer has a place in my graph
                    # delete edge + residual; will condition only ever raised on fwd edges
                    self.pop_edge(node, edge.node)

    #
    # def nodes(self):
    #     """Returns nodes in order of incoming edges (smallest first)"""
    #     def incoming_func(node):
    #         return len([edge for edge in self[node] if edge.residual])
    #
    #     incoming = [(node, incoming_func(node)) for node in self.graph.keys()]
    #     incoming.sort(key=lambda row: row[1], reverse=True)
    #     return [node for node, _ in incoming
