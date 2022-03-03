# coding=utf-8
from unittest import TestCase

from src.simplify.flow import Flow
from src.simplify.graph_objects import Vertex
from src.simplify.specialised_graph import FlowGraph, WeightedDigraph


class TestFlow(TestCase):
    def setUp(self) -> None:
        labels = ["a", "b", "c", "d", "e", "f"]
        self.vertices = [Vertex(ID, label=label) for ID, label in enumerate(labels)]
        a, b, c, d, e, f = self.vertices

        # set up weighted_graph and flow graphs
        self.flow_graph = FlowGraph(self.vertices)
        self.flow_graph.add_edge(a, (b, 10), (c, 10))
        self.flow_graph.add_edge(b, (d, 25))
        self.flow_graph.add_edge(c, (e, 25))
        self.flow_graph.add_edge(d, (f, 10))
        self.flow_graph.add_edge(e, (f, 10), (b, 6))

    def test_edmonds_karp(self):
        """Max flow test between nodes"""
        a, b, c, d, e, f = self.vertices

        expected = 20
        calculated = Flow.edmonds_karp(self.flow_graph, a, f)

        self.assertEqual(expected, calculated)


class TestSettling(TestCase):
    def setUp(self) -> None:
        # gen vertices
        people: list[Vertex] = []
        for ID, person in enumerate(["b", "c", "d", "e", "f", "g"]):
            people.append(Vertex(ID, label=person))
        b, c, d, e, f, g = people

        # build flow graph of transactions
        messy = FlowGraph(people)
        messy.add_edge(b, (c, 40))
        messy.add_edge(c, (d, 20))
        messy.add_edge(d, (e, 50))
        messy.add_edge(f, (e, 10), (d, 10), (c, 30), (b, 10))
        messy.add_edge(g, (b, 30), (d, 10))

        self.messy = messy

    def test_settle(self):
        """Ensures that we are settling properly

        Initial (9 edges, $210 changing hands)
            A ->
            B -> C, 40
            C -> D, 20
            D -> E, 50
            E ->
            F -> (E, 10), (D, 10), (C, 30), (B, 10)
            G -> (B, 30), (D, 10)

        Should settle to

            A ->
            B -> C, 40
            C -> D, 20
            D -> E, 50
            E ->
            F -> (E, 10), (C, 30)
            G -> B, 30


        Multiple valid clean orders depending on starting node, as graph changes as we operate on it
        """

        self.assertTrue(False)

    def test_paid(self):
        """Checks that everyone is paid enough"""

        def gets(graph: FlowGraph) -> dict[Vertex, int]:
            """Flow through a node"""
            return {node: graph.flow_through(node)[0] for node in graph.nodes()}

        def should_get(graph: FlowGraph):
            """Max capacity through a node"""
            return {node: graph.flow_through(node)[1] for node in graph.nodes()}

        # get initial weights in of everyone
        initial = should_get(self.messy)
        cleaned = gets(Flow.simplify_debt(self.messy))

        delta_i = sum(initial.values())
        delta_c = sum(cleaned.values())
        print(delta_i, delta_c)

        print(initial, cleaned, sep="\n")
        with self.subTest('Initial net flow'):
            self.assertEqual(0, delta_i)

        with self.subTest('Closed system'):
            self.assertEqual(0, delta_c)
