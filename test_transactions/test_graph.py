# coding=utf-8

from transactions.graph import *
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

    def test_nodes_not_in_graph(self):
        f = Vertex(6, "f")
        h = Vertex(7, "h")

        with self.assertRaises(GraphOpError):
            self.g.add_edge(f, h)

    def test_add_node(self):
        pre_add = str(self.g)
        self.g.add_node(Vertex(3, "a"))
        post_add = str(self.g)

        # print(pre_add, post_add, sep='\n')
        self.assertNotEqual(pre_add, post_add)

    def test_remove_node(self):
        pre_pop = str(self.g)
        self.g.remove_node(self.vertices[0])
        post_pop = str(self.g)

        print(pre_pop, post_pop, sep="\n")
        self.assertNotEqual(pre_pop, post_pop)


class TestBFS(TestCase):
    def test_BFSQueue(self):
        ...

    def setUp(self):
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

        # expected repr of ordering from this graph
        self.expected = "BFSDiscovered(a, e, g, c, b)"

    def test_search_successful(self):
        ordering = f"{self.g.BFS()!r}"

        self.assertEqual(ordering, self.expected)
