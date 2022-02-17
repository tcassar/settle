# coding=utf-8
from transactions.graph import *
from transactions.graph_ops import *
from unittest import TestCase


class TestBFS(TestCase):
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

        # expected repr of ordering from this graph
        self.expected = "BFSDiscovered(a, e, g, c, b)"

    def test_shortest_path(self):
        """
        Checks that we can in fact find shortest path along
        """

        a, b, c, d, e, f = self.vertices

        cases = ["digraph", "weighted", "flow"]

        # set up weighted and flow graphs
        weighted = WeightedDigraph(self.vertices)
        flow = FlowGraph(self.vertices)

        for g in [weighted, flow]:
            g.add_edge(a, (b, 10), (c, 10))
            g.add_edge(b, (d, 25))
            g.add_edge(c, (e, 25))
            g.add_edge(d, (f, 10))
            g.add_edge(e, (f, 10), (b, 6))

        # check precalulated shortest path
        graph_cases = [self.g, weighted, flow]

        for case, g in zip(cases, graph_cases):
            with self.subTest(case):
                calc_shorted: list[Vertex] = GraphOps.shortest_path(self.g, a, f)
                expected: list[Vertex] = [a, c, e, f]
                self.assertEqual(expected, calc_shorted)
