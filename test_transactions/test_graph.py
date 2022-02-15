# coding=utf-8

from transactions.digraph import *
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
        with self.subTest("Bad gen"), self.assertRaises(GraphOpError):
            _ = Digraph([1, 2, 3])  # type: ignore

        with self.subTest("Bad op"), self.assertRaises(GraphOpError):
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


class TestWeightedDigraph(TestCase):
    def setUp(self) -> None:
        labels = ["u", "v", "w"]
        self.vertices = [Vertex(ID, label=label) for ID, label in enumerate(labels)]
        u, v, w = self.vertices

        self.weighted_digraph = WeightedDigraph(self.vertices)
        self.weighted_digraph.add_edge(u, v, 12)
        self.weighted_digraph.add_edge(u, w, 4)
        self.weighted_digraph.add_edge(v, w, 7)

    def test_add_edge(self):
        pre_add = str(self.weighted_digraph)
        (
            u,
            v,
            w,
        ) = self.vertices
        self.weighted_digraph.add_edge(w, u, 9)
        post_add = str(self.weighted_digraph)

        print(pre_add, post_add, sep="\n")
        self.assertNotEqual(pre_add, post_add)

    def test_float_edge(self):
        (
            u,
            v,
            w,
        ) = self.vertices

        with self.assertRaises(GraphGenError):
            self.weighted_digraph.add_edge(v, u, 0.5)  # type: ignore

    def test_remove_node(self):

        pre_pop = str(self.weighted_digraph)
        self.weighted_digraph.remove_node(self.vertices[1])
        post_pop = str(self.weighted_digraph)

        print(pre_pop, post_pop, sep="\n")

        with self.subTest("valid"):
            self.assertNotEqual(pre_pop, post_pop)

        with (self.subTest("node not in list"), self.assertRaises(GraphOpError)):
            self.weighted_digraph.remove_node(Vertex(132, "v"))
