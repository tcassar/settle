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
        calc_shorted: list[Vertex] = GraphOps.shortest_path(self.g, a, f)
        expected: list[Vertex] = [a, c, e, f]

        self.assertEqual(expected, calc_shorted)
