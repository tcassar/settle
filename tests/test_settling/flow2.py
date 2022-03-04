# coding=utf-8
from unittest import TestCase

from src.simplify.flow2 import *
from src.simplify.graph_objects import Vertex


class TestFlowEdge(TestCase):
    """Tests for FlowEdge"""

    def setUp(self) -> None:
        self.edges = [FlowEdge(Vertex(0), 5 * n) for n in range(2)]
        self.edges[0].flow = -3  # => unused capacity should be three

    def test_unused_capacity(self):
        """builds two edges, residual and non-residual
        non-residual has capacity 5"""

        for edge, cap in zip(self.edges, [3, 5]):
            with self.subTest(edge):
                self.assertEqual(edge.unused_capacity(), cap)

    def test_push_flow(self):
        """Checks that we update flow by required amount"""
        capacity0 = {edge: edge.unused_capacity() for edge in self.edges}
        # push three units of capacity through each edge
        for edge, exp in zip(self.edges, [0, 2]):
            with self.subTest(edge):
                edge.push_flow(3)
                self.assertEqual(exp, edge.unused_capacity())

        # try to push excess amount of flow down an edge
        with self.subTest("exceed capacity"), self.assertRaises(FlowEdgeError):
            self.edges[1].push_flow(2)


class TestFlowGraph(TestCase):

    def setUp(self) -> None:
        # make some nodes for a graph
        self.nodes = [Vertex(n, label=chr(n + 97)) for n in range(5)]
        a, b, c, d, e = self.nodes
        self.graph = FlowGraph(self.nodes)

    def test_is_edge(self):
        a, b, c, d, e = self.nodes

        with self.subTest('no edge'):
            self.assertFalse(self.graph.is_edge(a, b))

        with self.subTest('edge'):
            self.graph.add_edge(a, b, 4)
            self.assertTrue(self.graph.is_edge(a, b))

    def test_add_edge(self):
        a, b, c, d, e = self.nodes
        # check there aren't edges
        with self.subTest('negative test'):
            self.assertFalse(self.graph.is_edge(a, b))
            self.assertFalse(self.graph.is_edge(b, a, residual=True))

        self.graph.add_edge(a, b, 5)

        with self.subTest('added'):
            self.assertTrue(self.graph.is_edge(a, b))
            self.assertTrue(self.graph.is_edge(b, a, residual=True))
            self.assertFalse(self.graph.is_edge(b, a))

    def test_remove_edge(self):
        a, b, c, d, e = self.nodes

        self.graph.add_edge(a, b, 5)

        with self.subTest('negative'):
            self.assertTrue(self.graph.is_edge(a, b))
            self.assertTrue(self.graph.is_edge(b, a, residual=True))

        self.graph.remove_edge(a, b)

        with self.subTest('removed edge'):
            self.assertFalse(self.graph.is_edge(a, b))
        with self.subTest('removed residual'):
            self.assertFalse(self.graph.is_edge(b, a, residual=True))