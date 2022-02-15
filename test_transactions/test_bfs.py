# coding=utf-8

from transactions.traversals import *
from unittest import TestCase


class TestBFS(TestCase):
    """Tests searching for BFS"""

    def setUp(self):
        # make a graph with 5 nodes

        labels = ["a", "b", "c", "g", "e"]
        self.vertices = [Vertex(ID, label=label) for ID, label in enumerate(labels)]

        self.g = Digraph(self.vertices)
        self.g_traversal = Traversals(self.g)
        a, b, c, d, e = self.vertices
        self.g.add_edge(a, b)
        self.g.add_edge(a, e)
        self.g.add_edge(b, c)
        self.g.add_edge(b, e)
        self.g.add_edge(d, c)
        self.g.add_edge(e, c)
        self.g.add_edge(e, d)

        # expected repr of ordering from this graph
        self.expected = "BFSDiscovered(a, e, g, c, b)"

    def test_search_successful(self):
        ordering = f"{self.g_traversal.BFS()!r}"

        self.assertEqual(ordering, self.expected)
