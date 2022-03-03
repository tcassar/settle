# coding=utf-8

from unittest import TestCase

from src.simplify.graph_objects import Vertex, Edge
from src.simplify.base_graph import Digraph, GraphError
from src.simplify.specialised_graph import WeightedDigraph, FlowGraph


class TestDigraph(TestCase):
    """Generate a digraph and some vertices"""

    def setUp(self) -> None:
        """Build basic graph"""
        labels = ["u", "v", "w"]
        self.vertices = [Vertex(ID, label=label) for ID, label in enumerate(labels)]

        self.graph = Digraph(self.vertices)
        u, v, w = self.vertices
        self.graph.add_edge(u, v, w)
        self.graph.add_edge(v, w)

    def test_init(self):
        expected = "U -> V, W, \nV -> W, \nW -> \n"

        with self.subTest("init"):
            self.assertEqual(expected, str(self.graph))

        with self.subTest("helpers"):
            self.assertTrue(self.graph.is_node(self.vertices[0]))
            self.assertTrue(self.graph.sanitize(*self.vertices))

            with self.assertRaises(GraphError):
                self.graph.edge_from_nodes(self.vertices[2], [Edge(self.vertices[0])])

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
        u, v, w = self.vertices

        print(self.graph)
        self.graph.pop_node(u)
        print(self.graph)
        self.assertFalse(self.graph.is_node(u))
        with self.assertRaises(GraphError):
            self.graph.edge_from_nodes(u, self.graph[v])

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

    def test_nodes(self):
        self.assertEqual(self.vertices, self.graph.nodes())


class TestWeightedDigraph(TestCase):
    def setUp(self) -> None:
        """Build basic graph"""
        labels = ["u", "v", "w"]
        self.vertices = [Vertex(ID, label=label) for ID, label in enumerate(labels)]

        self.graph = WeightedDigraph(self.vertices)
        u, v, w = self.vertices
        self.graph.add_edge(u, (v, 1), (w, 2))
        self.graph.add_edge(v, (w, 3))

    def test_add_edge(self):
        u, v, w = self.vertices
        self.assertFalse(self.graph.is_edge(w, v))
        self.graph.add_edge(w, (v, 4))
        self.assertTrue(self.graph.is_edge(w, v))

    def test_weighst_in(self):
        self.assertEqual(self.graph.weights_in(self.vertices[2]), 5)


class TestFlowGraph(TestCase):
    def setUp(self) -> None:
        """Build basic graph"""
        labels = ["u", "v", "w"]
        self.vertices = [Vertex(ID, label=label) for ID, label in enumerate(labels)]

        self.graph = FlowGraph(self.vertices)
        u, v, w = self.vertices
        self.graph.add_edge(u, (v, 1), (w, 2))
        self.graph.add_edge(v, (w, 3))

    def test_add_edge(self):
        print(self.graph)

    def test_pop_edge(self):
        u, v, w = self.vertices
        self.graph.pop_edge(u, v)

        # check normal graph
        self.assertFalse(self.graph.is_edge(u, v))
        # check residual graph
        self.assertFalse(self.graph.is_edge(v, u))

    def test_neighbours(self):
        u, v, w = self.vertices
        pre_flow = self.graph.flow_neighbours(u)
        # send 3 units from u -> v; hope is that v no longer appears as a neighbour
        self.graph.push_flow([u, v], 1)
        post_flow = self.graph.flow_neighbours(u)

        # expected neighbours
        self.assertEqual(set(self.graph.nodes_from_edges(pre_flow)), {v, w})

        # expected neighbours after flow
        # expected neighbours
        self.assertEqual(set(self.graph.nodes_from_edges(post_flow)), {w})

    def test_bottleneck(self):
        u, v, w = self.vertices

        self.assertEqual(1, self.graph.bottleneck([u, v, w]))

    def test_weights_in(self):
        self.assertEqual(self.graph.weights_in(self.vertices[2]), 5)
