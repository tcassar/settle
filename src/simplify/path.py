# coding=utf-8
import logging
import random
import sys
from dataclasses import dataclass
from typing import Callable

from ordered_set import OrderedSet

# initialise logger
import src.simplify.graph_objects
from src.simplify import base_graph as graphs

logging.basicConfig(stream=sys.stdout, encoding="utf-8", level=logging.DEBUG)


# typing
disc_map = dict[
    src.simplify.graph_objects.Vertex, src.simplify.graph_objects.Vertex | bool
]
"""disc_map used to track which nodes have been discovered; {node: discovered?}"""


prev_map = dict[
    src.simplify.graph_objects.Vertex, src.simplify.graph_objects.Vertex | None
]
"""prev_map used to track a path through a graph; stored as {node: comes_from_node}. 
If node has no links (i.e. is start node), value is None"""


class SearchError(Exception):
    def __init__(self, text, node: src.simplify.graph_objects.Vertex):
        super(SearchError, self).__init__(text, node)
        self.node = node


def void(
    current: src.simplify.graph_objects.Vertex,
    neighbour: src.simplify.graph_objects.Vertex,
) -> None:
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
    def __init__(self, *args: src.simplify.graph_objects.Vertex):
        self.data: OrderedSet[src.simplify.graph_objects.Vertex] = OrderedSet(args)

    def __str__(self):
        str_ = ""
        for datum in self.data:
            str_ += str(datum).upper()
        return str_

    def enqueue(self, *args: src.simplify.graph_objects.Vertex):
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
        graph: graphs.GenericDigraph,
        src: None | src.simplify.graph_objects.Vertex = None,
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
            # n = len(graph.graph)
            # start = list(graph.graph.keys())[random.randint(0, n - 1)]
            # queue.enqueue(start)
            start = next(iter(graph.graph))
            logging.debug(f"starting from {start}")

            # queue.enqueue(next(iter(graph.graph)))

        return queue, disc, prev

    @staticmethod
    def shortest_path(
        graph: graphs.GenericDigraph,
        source: src.simplify.graph_objects.Vertex,
        sink: src.simplify.graph_objects.Vertex,
        neighbours: Callable,
    ) -> list[src.simplify.graph_objects.Vertex]:
        """
        Uses a recursive implementation of BFS to find path between nodes
        Accepts graph, source node, sink node, returns list of nodes, which is the path from src to sink
        """

        # create queue, discovered list, previous list
        queue, discovered, prev = Path.build_bfs_structs(graph, source)

        # recursive call
        previous = Path.BFS(
            graph=graph,
            queue=queue,
            discovered=discovered,
            target=sink,
            previous=prev,
            neighbours=neighbours,
        )

        return Path._build_path(previous, sink)

    @staticmethod
    def _build_path(
        previous: prev_map, sink: src.simplify.graph_objects.Vertex
    ) -> list[src.simplify.graph_objects.Vertex]:
        """Given a mapping of previous nodes, reconstructs a path to sink"""
        path: list[src.simplify.graph_objects.Vertex] = [sink]

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
        target: src.simplify.graph_objects.Vertex | None,
        previous: prev_map,
        neighbours: Callable,
        do_to_neighbour: Callable = void,
    ) -> prev_map:
        """BFS Search as part of finding the shortest path through unweighted graph from src -> target.
        Target = None => walk through entire graph, terminate at empty queue
        Returns 'previous' list so that path can be rebuilt.
        Can pass in a function `do_to_neighbour` to do to all nodes during the BFS

        neighbour function need to return edge
        """
        # breakpoint: f"q: {queue}\n discovered: {str_map(discovered)}\nprev: {str_map(prev)}"

        # will only happen if no path to node
        if queue.is_empty():
            return previous

        else:
            # discover next node in queue
            current = queue.dequeue()
            discovered[current] = True

            # check we haven't been fed a standalone node (i.e. no forward or backwards links)
            if not graph.connected(current):
                if not queue:
                    raise SearchError("Cannot traverse a non connected node", current)

            # if discovered target node return prev
            if current == target:
                return previous

            else:
                # otherwise, continue on
                # enqueue neighbours, keep track of whose neighbours they are given not already discovered
                # do passed in function to neighbouring nodes
                for neighbour in neighbours(current):
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
                    neighbours=neighbours,
                    do_to_neighbour=do_to_neighbour,
                )
