# coding=utf-8
from transactions.graph import *
from transactions.graph_ops import *
from unittest import TestCase


class TestBFS(TestCase):
    """Tests searching for BFS"""

    def setUp(self):
        # make a graph with 5 nodes

        labels = ["a", "b", "c", "d", "e"]
        self.vertices = [Vertex(ID, label=label) for ID, label in enumerate(labels)]

        self.g = Digraph(self.vertices)
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

    def test_search_digraph(self):
        a, b, c, d, e = self.vertices
        print(GraphOps.shortest_path(self.g, a, d))

    def test_search_weighted(self):
        weighted = WeightedDigraph(self.vertices)
        a, b, c, d, e = self.vertices
        weighted.add_edge(a, b)


        print(GraphOps.shortest_path(self.g, a, b))