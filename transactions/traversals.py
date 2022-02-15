# coding=utf-8

from transactions.digraph import Digraph, Vertex

from ordered_set import OrderedSet


class SearchError(Exception):
    ...


class BFSStruct:
    """Base class for custom BFS data structures"""

    def __init__(self, *args):
        self.q = OrderedSet(args)

    def __len__(self):
        return len(self.q)


class BFSQueue(BFSStruct):
    """Standard queue, but does not allow the repetition of elements; also typed as only accepting vertices"""

    # def __bool__(self) -> bool:
    #     if len(self.q) == 0:
    #         return False
    #     else:
    #         return True

    def enqueue(self, *args: Vertex):
        for v in args:
            Digraph.sanitize(v)
            self.q.append(v)

    def dequeue(self):
        return self.q.pop()

    def is_empty(self) -> bool:
        return not len(self.q)


class BFSDiscovered(BFSStruct):
    def append(self, vertex: Vertex) -> None:
        Digraph.sanitize(vertex)
        _ = self.q.append(vertex)

    def __repr__(self):
        args = ""
        for v in self.q:
            args += str(v) + ", "
        return f"BFSDiscovered({args[:-2]})"


class Traversals:
    def __init__(self, graph: Digraph):
        self.graph = graph.graph

    def BFS(self) -> BFSDiscovered:
        """Public facing BFS; starts then returns BFSDiscovered"""

        # initialise queue and discovered list
        queue = BFSQueue()
        discovered = BFSDiscovered()

        # get arbitrary start node
        # will always be insertion order but doesn't need to be
        start = next(iter(self.graph))

        # enqueue initial node
        queue.enqueue(start)

        # recursive call
        # print(f'Queue: {queue}\nDiscovered{discovered}\n')
        out = self._recursiveBFS(queue, discovered)
        repr(out)
        return out

    def _recursiveBFS(self, queue: BFSQueue, discovered: BFSDiscovered) -> BFSDiscovered:  # type: ignore
        # print(f"Queue: {queue}\nDiscovered: {discovered}\n")

        if queue.is_empty():
            # print(f"returning {discovered!r}\n")
            return discovered

        else:
            # dequeue, mark as discovered
            current = queue.dequeue()
            discovered.append(current)

            # enqueue neighbours
            queue.enqueue(*self.graph[current])

            # bfs on new state

            return self._recursiveBFS(queue, discovered)
