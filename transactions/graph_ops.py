# coding=utf-8

import transactions.graph as graphs

from dataclasses import dataclass
from ordered_set import OrderedSet


@dataclass(init=False)
class BaseBFSStruct:
    def __init__(self, *args: graphs.Vertex):
        self.data: OrderedSet[graphs.Vertex] = OrderedSet(args)


class BFSQueue(BaseBFSStruct):
    def enqueue(self, *args: graphs.Vertex):
        for v in args:
            graphs.GenericDigraph.sanitize(v)
            self.data.append(v)

    def dequeue(self):
        return self.data.pop()

    def is_empty(self) -> bool:
        return not len(self.data)


class BFSDiscovered(BaseBFSStruct):
    def append(self, vertex: graphs.Vertex) -> None:
        graphs.GenericDigraph.sanitize(vertex)
        self.data.append(vertex)


class GraphOps:
    """Namespace for graph operations"""

    @staticmethod
    def is_path(
        graph: graphs.GenericDigraph, source: graphs.Vertex, sink: graphs.Vertex
    ) -> list[graphs.Vertex]:
        """Uses a recursive implementation of BFS to find path between nodes"""

        # create queue, discovered list
        queue = BFSQueue(source)
        discovered = BFSDiscovered()

        # recursive call
        return GraphOps._recursive_BFS(graph, queue, discovered, sink)

    @staticmethod
    def _recursive_BFS(graph: graphs.GenericDigraph, queue: BFSQueue, discovered: BFSDiscovered, target: graphs.Vertex
    ) -> list[graphs.Vertex]:
        """Does not account for weightings"""

        # will only happen if no path to node
        if queue.is_empty():
            return []

        else:
            # discover next node in queue
            current = queue.dequeue()
            discovered.append(current)

            # if discovered target node, return path from source
            if current == target:
                return list(discovered.data)

            else:
                # otherwise continue on
                # enqueue neighbours
                for neighbour in graph.graph[current]:
                    queue.enqueue(neighbour.node)

                # recursive call on new state
                return GraphOps._recursive_BFS(graph, queue, discovered, target)
