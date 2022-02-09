# coding=utf-8

from transactions.graph import Vertex, Digraph
from unittest import TestCase


class TestDigraph(TestCase):
    """Tests basic functionality of the digraph"""

    def setUp(self) -> None:
        """Build basic graph"""
        labels = ["u", "v", "w"]
        self.vertices = [Vertex(ID, label=label) for ID, label in enumerate(labels)]

        self.d = Digraph(self.vertices)
        u, v, w = self.vertices
        self.d.add_edge(u, v)
        self.d.add_edge(u, w)
        self.d.add_edge(v, w)

    def test_init(self):
        expected = """U -> V, W, \nV -> W, \nW -> \n"""
        self.assertEqual(str(self.d), expected)

    def test_is_edge(self):
        u, v, w = self.vertices

        yes = self.d.is_edge(u, v)
        no = self.d.is_edge(w, u)

        for case, expected, received in zip(
            ["exists", "doesn't exist"], [True, False], [yes, no]
        ):
            with self.subTest(case):
                self.assertIs(expected, received)

    def test_add_edge(self):
        *_, v, w = self.vertices
        d = self.d

        assert d.is_edge(w, v) is False
        d.add_edge(w, v)
        self.assertTrue(d.is_edge(w, v))

    def test_remove_edge(self):
        u, *_, w = self.vertices
        d = self.d

        assert d.is_edge(u, w) is True
        d.remove_edge(u, w)
        self.assertFalse(d.is_edge(u, w))

    def test_bad_vertex(self):
        ...
