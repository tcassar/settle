# coding=utf-8
from dataclasses import dataclass
from unittest import TestCase

from src.simplify.graph_objects import Vertex
from src.simplify.path import Path, prev_map, disc_map, BFSQueue
from src.simplify.base_graph import Digraph
from src.simplify.specialised_graph import WeightedDigraph, FlowGraph


class TestPath(TestCase):
    """Tests searching for BFS"""

    def setUp(self):
        # make a graph with 5 nodes

        labels = ["a", "b", "c", "d", "e", "f"]
        self.vertices = [Vertex(ID, label=label) for ID, label in enumerate(labels)]

        self.g = Digraph(self.vertices)
        a, b, c, d, e, f = self.vertices
        self.g.add_edge(a, b, c)
        self.g.add_edge(b, d)
        self.g.add_edge(d, f)
        self.g.add_edge(c, e)
        self.g.add_edge(d, f)
        self.g.add_edge(e, f, b)

        # set up weighted_graph and flow graphs
        self.weighted_graph = WeightedDigraph(self.vertices)
        self.flow_graph = FlowGraph(self.vertices)

        for g in [self.weighted_graph, self.flow_graph]:
            g.add_edge(a, (b, 10), (c, 10))
            g.add_edge(b, (d, 25))
            g.add_edge(c, (e, 25))
            g.add_edge(d, (f, 10))
            g.add_edge(e, (f, 10), (b, 6))

    def test_shortest_path(self):
        """
        Checks that we can in fact find shortest path along
        """

        a, b, c, d, e, f = self.vertices

        cases = ["digraph", "weighted_graph", "flow"]

        # check precalulated shortest path
        graph_cases = [self.g, self.weighted_graph, self.flow_graph]

        for case, g in zip(cases, graph_cases):
            with self.subTest(case):
                calc_shorted: list[Vertex] = Path.shortest_path(
                    self.g, a, f, self.g.neighbours
                )
                expected: list[Vertex] = [a, c, e, f]
                self.assertEqual(expected, calc_shorted)

    def test_build_path(self):
        """Given a prev_map, check we build the right path"""

        # generate vertices, unpack into vars
        vertices = []
        for ID, name in enumerate(["A", "B", "C", "D", "E", "F"]):
            vertices.append(Vertex(ID, name))

        a, c, b, d, e, f = vertices

        # build a prev map. for context, path is A -> B -> D -> F
        prev: prev_map = {a: None, b: a, c: a, d: b, e: c, f: d}
        expected = [a, b, d, f]

        self.assertEqual(expected, Path._build_path(prev, f))

    def test_recursive_bfs(self):
        """Check that BFS is finding paths along graph correctly"""
        graph = self.flow_graph
        a, b, c, d, e, f = graph.nodes()

        expected: prev_map = {a: None, b: a, c: a, d: b, e: c, f: e}

        # set up structures for BFS
        # create queue, discovered list, previous list
        queue = BFSQueue(next(iter(graph.graph)))

        discovered: disc_map = {node: False for node in graph.nodes()}
        prev: prev_map = {node: None for node in graph.nodes()}

        self.assertEqual(
            expected,
            Path.BFS(
                graph=graph,
                queue=queue,
                discovered=discovered,
                target=None,
                previous=prev,
                neighbours=graph.neighbours,
            ),
        )

    def test_find_target(self):
        graph = self.flow_graph
        a, b, c, *_ = graph.nodes()

        expected = {node: None for node in graph.nodes()}
        expected[b] = a
        expected[c] = a

        queue, discovered, previous = Path.build_bfs_structs(graph, a)

        calculated = Path.BFS(
            graph=graph,
            queue=queue,
            discovered=discovered,
            previous=previous,
            target=b,
            neighbours=graph.neighbours,
        )
        self.assertEqual(expected, calculated)

    def test_build_bfs_struct(self):
        with self.subTest("with initial value"):
            queue, disc, prev = Path.build_bfs_structs(
                self.flow_graph, self.vertices[0]
            )
            self.assertEqual(queue, BFSQueue(self.vertices[0]))

        with self.subTest("with initial value"):
            queue, disc, prev = Path.build_bfs_structs(self.flow_graph)
            self.assertEqual(queue, BFSQueue())

    def test_edges_hit(self):
        """Make sure that every edge is being considered"""
        # do a bfs, adding 1 to a count every time we touch an edge
        # do this for all possible start positions

        # FIXME: instead of walking through graph to do all edges, write a get_edges method, iterate through that list

        @dataclass
        class Counter:
            n: int = 0

            def count(self):
                self.n += 1

        def count_edge(current: Vertex, neighbour: Vertex) -> None:
            """Counts an edge"""
            counter.count()

        for graph in [self.g, self.weighted_graph, self.flow_graph]:
            for start in self.vertices:
                counter = Counter()
                queue, discovered, previous = Path.build_bfs_structs(graph, start)
                Path.BFS(
                    graph=graph,
                    queue=queue,
                    discovered=discovered,
                    target=None,
                    previous=previous,
                    neighbours=graph.neighbours,
                    do_to_neighbour=count_edge,
                )

                with self.subTest(f"graph: {graph}, starting at {start}"):
                    self.assertEqual(counter.n, 7)
