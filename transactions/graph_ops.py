# coding=utf-8

import transactions.graph as graphs

from dataclasses import dataclass
from ordered_set import OrderedSet

# typing
disc_map = dict[graphs.Vertex, graphs.Vertex | bool]
prev_map = dict[graphs.Vertex, graphs.Vertex | None]


def str_map(generic_map: disc_map | prev_map) -> str:
    """"""
    str_rep = ''
    for node, prev in generic_map.items():
        str_rep += f'{node}: {prev},\n'.upper()
    return str_rep


@dataclass(init=False)
class BFSQueue:
    def __init__(self, *args: graphs.Vertex):
        self.data: OrderedSet[graphs.Vertex] = OrderedSet(args)

    def __str__(self):
        str_ = ''
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


class GraphOps:
    """Namespace for graph operations"""

    @staticmethod
    def shortest_path(
            # todo: fix
            graph: graphs.GenericDigraph,
            source: graphs.Vertex,
            sink: graphs.Vertex,
    ) -> list[graphs.Vertex]:
        """Uses a recursive implementation of BFS to find path between nodes"""

        # create queue, discovered list, previous list
        queue = BFSQueue(source)

        discovered: disc_map = {node: False for node in graph.graph.keys()}
        prev: prev_map = {node: None for node in graph.graph.keys()}

        # recursive call
        previous = GraphOps._recursive_BFS(graph, queue, discovered, sink, prev)
        # print(str_map(previous))

        return GraphOps._build_path(previous, source, sink)

    @staticmethod
    def _build_path(previous: prev_map, source: graphs.Vertex, sink: graphs.Vertex) -> list[graphs.Vertex]:
        path: list[graphs.Vertex] = [sink]

        while current := previous[path[0]]:
            path.insert(0, current)

        assert path[0] == source
        return path


    @staticmethod
    def _recursive_BFS(
            graph: graphs.GenericDigraph,
            queue: BFSQueue,
            discovered: disc_map,
            target: graphs.Vertex,
            prev: prev_map,
    ) -> prev_map:
        """BFS Search as part of finding shortest path through unweighted graph. Returns 'previous' list so that
        path can be rebuilt"""

        # breakpoint: f"q: {queue}\n discovered: {str_map(discovered)}\nprev: {str_map(prev)}"

        # will only happen if no path to node
        if queue.is_empty():
            return prev

        else:
            # discover next node in queue
            current = queue.dequeue()
            discovered[current] = True

            # if discovered target node return prev
            if current == target:
                return prev

            else:
                # otherwise, continue on
                # enqueue neighbours, keep track of whose neighbours they are given not already discovered
                for neighbour in graph.neighbours(current):
                    if not discovered[neighbour.node]:
                        prev[neighbour.node] = current
                        queue.enqueue(neighbour.node)

                # recursive call on new state
                return GraphOps._recursive_BFS(graph, queue, discovered, target, prev)
