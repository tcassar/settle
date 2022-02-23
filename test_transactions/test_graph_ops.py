# coding=utf-8
from unittest import TestCase

from transactions.graph import *
from transactions.graph_ops import *


class TestGraphOps(TestCase):
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
                calc_shorted: list[Vertex] = Path.shortest_path(self.g, a, f)
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
        a, b, c, d, e, f = list(graph.graph.keys())

        expected: prev_map = {a: None, b: a, c: a, d: b, e: c, f: e}

        # set up structures for BFS
        # create queue, discovered list, previous list
        queue = BFSQueue(next(iter(graph.graph)))

        discovered: disc_map = {node: False for node in graph.nodes()}
        prev: prev_map = {node: None for node in graph.nodes()}

        self.assertEqual(
            expected,
            Path._recursive_BFS(
                graph=graph, queue=queue, discovered=discovered, prev=prev, target=f
            ),
        )

    def test_stepwise_bfs(self):
        ...

    def test_edmonds_karp(self):
        a, b, c, d, e, f = self.vertices

        expected = 20
        calculated = Flow.edmonds_karp(self.flow_graph, a, f)

        self.assertEqual(expected, calculated)

    #
    # def test_settle(self):
    #     people = ["Bob", "Charlie", "Dan", "Emma", "Fred", "George"]
    #     vertices: list[Vertex] = []
    #     # Generate vertices
    #     for ID, name in enumerate(people):
    #         vertices.append(Vertex(ID, name))
    #
    #     b, c, d, e, f, g = vertices
    #
    #     # represent debts in graph form
    #     debt_graph = FlowGraph(vertices)
    #     debt_graph.add_edge(b, (c, 40))
    #     debt_graph.add_edge(c, (d, 20))
    #     debt_graph.add_edge(d, (e, 50))
    #     debt_graph.add_edge(f, (e, 10), (d, 10), (c, 30), (b, 10))
    #     debt_graph.add_edge(g, (b, 30), (d, 10))
    #
    #
    #     simplified = Flow.simplify_debt(debt_graph)
