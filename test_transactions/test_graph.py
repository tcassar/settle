# coding=utf-8

from transactions.graph import *
from unittest import TestCase


class TestDigraph(TestCase):
    """Generate a digraph and some vertices"""

    def setUp(self) -> None:
        """Build basic graph"""
        labels = ["u", "v", "w"]
        self.vertices = [Vertex(ID, label=label) for ID, label in enumerate(labels)]

        self.graph = Digraph(self.vertices)
        u, v, w = self.vertices
        self.graph.add_edge(u, v)
        self.graph.add_edge(u, w)
        self.graph.add_edge(v, w)

    def test_init(self):
        expected = "U -> V, W, \nV -> W, \nW -> \n"

        with self.subTest("init"):
            self.assertEqual(expected, str(self.graph))

        with self.subTest("helpers"):
            self.assertTrue(self.graph.is_node(self.vertices[0]))
            self.assertTrue(self.graph.sanitize(*self.vertices))
            self.assertIsNotNone(
                self.graph.node_in_list(self.vertices[0], [Edge(self.vertices[0])])
            )

    def test_is_edge(self):
        u, v, w = self.vertices

        with self.subTest("is edge"):
            self.assertTrue(self.graph.is_edge(u, v))
        with self.subTest("isn't edge"):
            self.assertFalse(self.graph.is_edge(w, v))

    def test_add_node(self):

        new = Vertex(4, "b")
        self.assertFalse(self.graph.is_node(new))

        self.graph.add_node(new)
        self.assertTrue(self.graph.is_node(new))

    def test_pop_node(self):
        self.graph.pop_node(self.vertices[-1])
        self.assertFalse(self.graph.is_node(self.vertices[-1]))

    def test_pop_edge(self):
        u, v, w = self.vertices
        self.assertTrue(self.graph.is_edge(u, v))
        self.graph.pop_edge(u, v)

        self.assertFalse(self.graph.is_edge(u, v))

    def test_add_edge(self):
        u, v, w = self.vertices
        self.assertFalse(self.graph.is_edge(w, v))
        self.graph.add_edge(w, v)

        self.assertTrue(self.graph.is_edge(w, v))


class TestWeightedDigraph(TestCase):
    def setUp(self) -> None:
        """Build basic graph"""
        labels = ["u", "v", "w"]
        self.vertices = [Vertex(ID, label=label) for ID, label in enumerate(labels)]

        self.graph = WeightedDigraph(self.vertices)
        u, v, w = self.vertices
        self.graph.add_edge(u, v, 1)
        self.graph.add_edge(u, w, 2)
        self.graph.add_edge(v, w, 3)

    def test_init(self):
        expected = "U -> V[1], W[2], \nV -> W[3], \nW -> \n"

        with self.subTest("init"):
            self.assertEqual(expected, str(self.graph))

        with self.subTest("helpers"):
            self.assertTrue(self.graph.is_node(self.vertices[0]))
            self.assertTrue(self.graph.sanitize(*self.vertices))
            self.assertIsNotNone(
                self.graph.node_in_list(self.vertices[0], [Edge(self.vertices[0])])
            )

    def test_is_edge(self):
        u, v, w = self.vertices

        with self.subTest("is edge"):
            self.assertTrue(self.graph.is_edge(u, v))
        with self.subTest("isn't edge"):
            self.assertFalse(self.graph.is_edge(w, v))

    def test_add_node(self):
        new = Vertex(4, "b")
        self.assertFalse(self.graph.is_node(new))

        self.graph.add_node(new)
        self.assertTrue(self.graph.is_node(new))

    def test_pop_node(self):
        self.graph.pop_node(self.vertices[-1])
        self.assertFalse(self.graph.is_node(self.vertices[-1]))

    def test_pop_edge(self):
        u, v, w = self.vertices
        self.assertTrue(self.graph.is_edge(u, v))
        self.graph.pop_edge(u, v)

        self.assertFalse(self.graph.is_edge(u, v))

    def test_add_edge(self):
        u, v, w = self.vertices
        self.assertFalse(self.graph.is_edge(w, v))
        self.graph.add_edge(w, v, 4)

        self.assertTrue(self.graph.is_edge(w, v))
