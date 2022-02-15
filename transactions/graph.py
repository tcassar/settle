# coding=utf-8

"""
Set up graph object to be used in condensing debt settling
"""
from dataclasses import dataclass
from ordered_set import OrderedSet

"""
Adj list vs matrix;

Matrix only con is space complexity is O(v^2); no new nodes will be added once graph is generated
List con is edge queries are O(V) instead of O(1) like with adj. matrix
"""


class GraphGenError(Exception):
    ...


class SearchError(Exception):
    ...


@dataclass
class Vertex:
    """Representation of a vertex; carries data and ID"""

    ID: int  # IDs should be unique
    label: str = ""  # optional label

    def _key(self) -> tuple:
        """Returns immutable repr of object for hashing"""
        return self.ID, self.label

    def __str__(self):
        return self.label

    def __hash__(self):
        """for adding to lists / dicts"""
        return hash(bytes(f"{self._key()}".encode("utf8")))

    def __iter__(self):
        return self


class BFSStruct:
    """Base class for custom BFS data structures"""

    def __init__(self, *args):
        self.q = OrderedSet(args)

    def __len__(self):
        return len(self.q)

    def __str__(self):
        return str(self.q)


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


class Digraph:
    """
    Simple graph; no weighting of edges, edges directional
    given no of vertices on init, edges can be added with .add_edge(src, dest)
    """

    def __init__(self, vertices: list[Vertex]) -> None:
        """
        Sets up a graph given a list of vertices
        """
        # initialise with values being empty
        # build dict checking each type as we go
        self.graph: dict[Vertex, list[Vertex]] = {
            vertex: [] if self.sanitize(vertex) else None  # type: ignore
            for vertex in vertices
        }

    def __str__(self):
        """Pretty print graph"""
        out = ""
        for node, adj_list in self.graph.items():
            pretty_nodes = ""
            for mapped_node in adj_list:
                pretty_nodes += f"{str(mapped_node).upper()}, "
            out += f"{str(node).upper()} -> {pretty_nodes}\n"

        return out

    @staticmethod
    def sanitize(v: Vertex, *args) -> bool:
        if args is not None:
            tests = [v, *args]
        else:
            tests = [v]
        for test in tests:
            if type(test) is not Vertex:
                raise GraphGenError(f"{test} if of type {type(test)} not Vertex ")
        return True

    def add_edge(self, src: Vertex, dest: Vertex) -> None:
        """Adds edge from src  -> destination; **directional**"""
        self.sanitize(src, dest)
        self.graph[src].append(dest)

    def remove_edge(self, src: Vertex, dest: Vertex) -> None:
        """removes dest from src's adj list"""
        self.sanitize(src, dest)
        self.graph[src].remove(dest)

    def is_edge(self, src: Vertex, dest: Vertex) -> bool:
        self.sanitize(src, dest)
        return dest in self.graph[src]

    def BFS(self) -> OrderedSet[Vertex]:
        """Public facing BFS; starts then returns list at end"""

        # initialise queue and discovered list
        queue = BFSQueue()
        discovered = BFSDiscovered()

        # get arbitrary start node
        # will always be insertion order but doesn't need to be
        start = next(iter(self.graph))

        # enqueue initial node
        queue.enqueue(start)

        # recursive call
        print(f'Queue: {queue}\nDiscovered{discovered}\n')
        return self._recursiveBFS(queue, discovered)

    def _recursiveBFS(self, queue: BFSQueue, discovered: BFSDiscovered) -> OrderedSet[Vertex]:
        print(f'Queue: {queue}\nDiscovered{discovered}')

        if queue.is_empty():
            return discovered.q

        else:
            # dequeue, mark as discovered
            current = queue.dequeue()
            discovered.append(current)

            # enqueue neighbours
            queue.enqueue(*self.graph[current])

            # bfs on new state
            print(f'Queue: {queue}\nDiscovered{discovered}')
            self._recursiveBFS(queue, discovered)
