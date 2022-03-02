# coding=utf-8
from unittest import TestCase

from transactions.graph import *
from transactions.graph_ops import *


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
                calc_shorted: list[Vertex] = Path.shortest_path(self.g, a, f, self.g.neighbours)
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
                neighbours=graph.neighbours
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
            graph=graph, queue=queue, discovered=discovered, previous=previous, target=b, neighbours=graph.neighbours
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


class TestFlow(TestCase):
    def setUp(self) -> None:
        labels = ["a", "b", "c", "d", "e", "f"]
        self.vertices = [Vertex(ID, label=label) for ID, label in enumerate(labels)]
        a, b, c, d, e, f = self.vertices

        # set up weighted_graph and flow graphs
        self.flow_graph = FlowGraph(self.vertices)
        self.flow_graph.add_edge(a, (b, 10), (c, 10))
        self.flow_graph.add_edge(b, (d, 25))
        self.flow_graph.add_edge(c, (e, 25))
        self.flow_graph.add_edge(d, (f, 10))
        self.flow_graph.add_edge(e, (f, 10), (b, 6))

    def test_edmonds_karp(self):
        """Max flow test between nodes"""
        a, b, c, d, e, f = self.vertices

        expected = 20
        calculated = Flow.edmonds_karp(self.flow_graph, a, f)

        self.assertEqual(expected, calculated)

    def test_settle(self):
        """Ensures that we are settling properly

        Initial (9 edges, $210 changing hands)
            A ->
            B -> C, 40
            C -> D, 20
            D -> E, 50
            F -> (E, 10), (D, 10), (C, 30), (B, 10)
            G -> (B, 30), (D, 10)

        Multiple valid clean orders depending on starting node, as graph changes as we operate on it
        """

        # gen vertices
        people: list[Vertex] = []
        for ID, person in enumerate(["b", "c", "d", "e", "f", "g"]):
            people.append(Vertex(ID, label=person))
        b, c, d, e, f, g = people

        # build flow graph of transactions
        messy = FlowGraph(people)
        messy.add_edge(b, (c, 40))
        messy.add_edge(c, (d, 20))
        messy.add_edge(d, (e, 50))
        messy.add_edge(f, (e, 10), (d, 10), (c, 30), (b, 10))
        messy.add_edge(g, (b, 30), (d, 10))

        # build expected clean graph
        ex_clean = WeightedDigraph(people)
        ex_clean.add_edge(b, (c, 10))
        ex_clean.add_edge(d, (e, 40))
        ex_clean.add_edge(f, (e, 20), (c, 40))
        ex_clean.add_edge(g, (b, 10), (d, 30))

        # clean graph
        got_clean: WeightedDigraph = Flow.simplify_debt(messy)

        print(f'expected:\n{ex_clean}\nreceived:\n{got_clean}')

