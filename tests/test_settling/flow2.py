# coding=utf-8
from unittest import TestCase

from src.simplify.flow2 import *
from src.simplify.graph_objects import Vertex


class TestFlowEdge(TestCase):
    """Tests for FlowEdge"""

    def test_unused_capacity(self):
        # builds two edges, residual and non-residual
        # non-residual has capacity 5
        edges = [FlowEdge(Vertex(0), 5*n) for n in range(2)]
        edges[0].flow = -3  # => unused capacity should be three
        for edge, cap in zip(edges, [3, 5]):
            with self.subTest(edge):
                self.assertEqual(edge.unused_capacity(), cap)

        