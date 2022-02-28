# coding=utf-8

import transactions.graph as graphs
from transactions.graph import FlowGraph

import copy
from dataclasses import dataclass
from ordered_set import OrderedSet
from typing import Callable


# typing
disc_map = dict[graphs.Vertex, graphs.Vertex | bool]
"""disc_map used to track which nodes have been discovered; {node: discovered?}"""


prev_map = dict[graphs.Vertex, graphs.Vertex | None]
"""prev_map used to track a path through a graph; stored as {node: comes_from_node}. 
If node has no links (i.e. is start node), value is None"""


class SearchError(Exception):
    ...


def void(current: graphs.Vertex, neighbour: graphs.Vertex) -> None:
    """Placeholder for a plain bfs; allows adding functionality such as a maxflow along each edge during a BFS"""
    pass


def str_map(generic_map: disc_map | prev_map) -> str:
    """"""
    str_rep = ""
    for node, prev in generic_map.items():
        str_rep += f"{node}: {prev},\n".upper()
    return str_rep


@dataclass(init=False)
class BFSQueue:
    def __init__(self, *args: graphs.Vertex):
        self.data: OrderedSet[graphs.Vertex] = OrderedSet(args)

    def __str__(self):
        str_ = ""
        for datum in self.data:
            str_ += str(datum).upper()
        return str_

    def enqueue(self, *args: graphs.Vertex):
        for v in args:
            graphs.GenericDigraph.sanitize(v)
            self.data.append(v)

    def dequeue(self):
        return self.data.pop(0)

    def is_empty(self) -> bool:
        return not len(self.data)


class Path:
    """Namespace for graph operations to do with walking through graph"""

    """Shortest path code: returns list[Vertex], hops along a path"""

    @staticmethod
    def build_bfs_structs(
        graph: graphs.GenericDigraph, src: None | graphs.Vertex = None
    ) -> tuple[BFSQueue, disc_map, prev_map]:
        """Helper function to initialise prev_map, disc_map and bfs queue;
        if source is passed then queue initialised with src"""
        queue = BFSQueue()
        disc: disc_map = {node: False for node in graph.nodes()}
        prev: prev_map = {node: None for node in graph.nodes()}

        if src:
            queue.enqueue(src)
        else:
            # get 'first' item from graph
            queue.enqueue(next(iter(graph.graph)))

        return queue, disc, prev

    @staticmethod
    def shortest_path(
        graph: graphs.GenericDigraph,
        source: graphs.Vertex,
        sink: graphs.Vertex,
    ) -> list[graphs.Vertex]:
        """
        Uses a recursive implementation of BFS to find path between nodes
        Accepts graph, source node, sink node, returns list of nodes, which is the path from src to sink
        """

        # create queue, discovered list, previous list
        queue, discovered, prev = Path.build_bfs_structs(graph, source)

        # recursive call
        previous = Path.BFS(
            graph=graph, queue=queue, discovered=discovered, target=sink, previous=prev
        )
        # print(str_map(previous))

        return Path._build_path(previous, sink)

    @staticmethod
    def _build_path(previous: prev_map, sink: graphs.Vertex) -> list[graphs.Vertex]:
        """Given a mapping of previous nodes, reconstructs a path to sink"""
        path: list[graphs.Vertex] = [sink]

        while current := previous[path[0]]:
            path.insert(0, current)

        if path[0] == sink:
            path = []

        return path

    @staticmethod
    def BFS(
        *,
        graph: graphs.GenericDigraph,
        queue: BFSQueue,
        discovered: disc_map,
        target: graphs.Vertex | None,
        previous: prev_map,
        do_to_neighbour: Callable = void,
    ) -> prev_map:
        """BFS Search as part of finding the shortest path through unweighted graph from src -> target.
        Target = None => walk through entire graph, terminate at empty queue
        Returns 'previous' list so that path can be rebuilt.
        Can pass in a function `do_to_neighbour` to do to all nodes during the BFS"""

        # breakpoint: f"q: {queue}\n discovered: {str_map(discovered)}\nprev: {str_map(prev)}"

        # will only happen if no path to node
        if queue.is_empty():
            return previous

        else:
            # discover next node in queue
            current = queue.dequeue()
            discovered[current] = True

            # if discovered target node return prev
            if current == target:
                return previous

            else:
                # otherwise, continue on
                # enqueue neighbours, keep track of whose neighbours they are given not already discovered
                # do passed in function to neighbouring nodes
                for neighbour in graph.neighbours(current):
                    if not discovered[neighbour.node]:
                        previous[neighbour.node] = current
                        queue.enqueue(neighbour.node)

                    do_to_neighbour(current, neighbour.node)

                # recursive call on new state
                return Path.BFS(
                    graph=graph,
                    queue=queue,
                    discovered=discovered,
                    target=target,
                    previous=previous,
                    do_to_neighbour=do_to_neighbour
                )


class Flow:
    """Namespace for all flow operations"""

    @staticmethod
    def edmonds_karp(
        graph: FlowGraph, source: graphs.Vertex, sink: graphs.Vertex
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
        graph: FlowGraph, u: graphs.Vertex, v: graphs.Vertex
    ) -> list[graphs.Vertex]:
        return Path.shortest_path(graph, u, v)

    @staticmethod
    def augment_path(graph: FlowGraph, path: list[graphs.Vertex], bottleneck: int):
        """Push flow down path, push flow up residual paths"""
        residual_path = copy.deepcopy(path)
        residual_path.reverse()

        graph.push_flow(path, bottleneck)
        graph.push_flow(residual_path, bottleneck * -1)

    @staticmethod
    def simplify_debt(messy: graphs.FlowGraph) -> graphs.WeightedDigraph:
        """One round of graph simplification; done by walking through graph w/ BFS,
        applying maxflow to every neighbour in graph"""

        def get_max(src: graphs.Vertex, sink: graphs.Vertex) -> int:
            """Helper to improve readability. Gets max flow between src and sink"""
            return Flow.edmonds_karp(messy, src, sink)

        def cleanup(current: graphs.Vertex, neighbour: graphs.Vertex) -> None:
            """To be passed into bfs
            calculates max flow from current -> neighbour, adds edge to clean with that weight"""
            # print(f'currently at {current}')

            flow = get_max(current, neighbour)
            # print(f'{flow} from {current} -> {neighbour}')
            if flow:
                clean.add_edge(current, (neighbour, flow))

        # create clean graph with no edges
        clean = graphs.WeightedDigraph(messy.nodes())

        # build queue, discovered hash map and prev hash maps
        queue, discovered, previous = Path.build_bfs_structs(messy)

        Path.BFS(
            graph=messy,
            queue=queue,
            discovered=discovered,
            target=None,
            previous=previous,
            do_to_neighbour=cleanup  # FIXME: function isnt running when passed in, but void is
        )

        print(f'finished bfs')

        return clean
