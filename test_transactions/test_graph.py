# coding=utf-8

from transactions.graph import Vertex, Digraph, GraphGenError
from unittest import TestCase


class TestDigraph(TestCase):
    """Tests basic functionality of the digraph"""

    def setUp(self) -> None:
        """Build basic graph"""
        labels = ["u", "v", "w"]
        self.vertices = [Vertex(ID, label=label) for ID, label in enumerate(labels)]

        self.g = Digraph(self.vertices)
        u, v, w = self.vertices
        self.g.add_edge(u, v)
        self.g.add_edge(u, w)
        self.g.add_edge(v, w)

    def test_init(self):
        expected = """U -> V, W, \nV -> W, \nW -> \n"""
        self.assertEqual(str(self.g), expected)

    def test_is_edge(self):
        u, v, w = self.vertices

        yes = self.g.is_edge(u, v)
        no = self.g.is_edge(w, u)

        for case, expected, received in zip(
            ["exists", "doesn't exist"], [True, False], [yes, no]
        ):
            with self.subTest(case):
                self.assertIs(expected, received)

    def test_add_edge(self):
        *_, v, w = self.vertices
        d = self.g

        assert d.is_edge(w, v) is False
        d.add_edge(w, v)
        self.assertTrue(d.is_edge(w, v))

    def test_remove_edge(self):
        u, *_, w = self.vertices
        d = self.g

        assert d.is_edge(u, w) is True
        d.remove_edge(u, w)
        self.assertFalse(d.is_edge(u, w))

    def test_bad_vertex(self):
        with self.subTest("Bad gen"), self.assertRaises(GraphGenError):
            _ = Digraph([1, 2, 3])  # type: ignore

        with self.subTest("Bad op"), self.assertRaises(GraphGenError):
            self.g.is_edge(1, 2)  # type: ignore


class TestBFS(TestCase):
    def test_BFSQueue(self):
        ...

    def test_BFS_visited(self):
        # make a graph with 5 nodes

        labels = ["a", "b", "c", "g", "e"]
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

        ordering = f"{self.g.BFS()!r}"
        expected = "BFSDiscovered(a, e, g, c, b)"

        self.assertEqual(ordering, expected)
