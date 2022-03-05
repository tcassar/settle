# coding=utf-8
from unittest import TestCase

from src.simplify.flow import Flow, Path
from src.simplify.graph_objects import Vertex, FlowEdge
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

    def test_flow_through(self):
        ...

    def test_2(self):
        nodes = [Vertex(0, label="src"), Vertex(10, label="sink")]
        nodes += [Vertex(n, label=chr(n + 96)) for n in range(1, 10)]
        tg = FlowGraph(nodes)

        s, t, a, b, c, d, e, f, g, h, i = tg.nodes()

        tg.add_edge(s, (a, 5), (b, 10), (c, 5))
        tg.add_edge(a, (d, 10))
        tg.add_edge(b, (a, 15), (e, 20))
        tg.add_edge(c, (f, 10))
        tg.add_edge(d, (e, 25), (g, 10))
        tg.add_edge(e, (c, 5), (h, 30))
        tg.add_edge(f, (h, 5), (i, 5))
        tg.add_edge(g, (t, 5))
        tg.add_edge(h, (t, 15), (i, 5))
        tg.add_edge(i, (t, 10))

        max_flow = Flow.edmonds_karp(tg, s, t)
        tg.to_dot()

        self.assertEqual(max_flow, 20)


class TestSettling(TestCase):
    def setUp(self) -> None:
        # gen vertices
        people: list[Vertex] = []
        for ID, person in enumerate(["b", "c", "d", "e", "f", "g"]):
            people.append(Vertex(ID, label=person))
        b, c, d, e, f, g = people

        # build flow graph of transactions
        messy = FlowGraph(people)
        messy_as_digraph = WeightedDigraph(messy.nodes())

        for graph in [messy, messy_as_digraph]:
            graph.add_edge(b, (c, 40))
            graph.add_edge(c, (d, 20))
            graph.add_edge(d, (e, 50))
            graph.add_edge(f, (e, 10), (d, 10), (c, 30), (b, 10))
            graph.add_edge(g, (b, 30), (d, 10))

        self.messy = messy
        self.messy_as_digraph = messy_as_digraph

    def test_simplify(self):
        """Ensures that we are settling properly

        Initial (9 edges, $210 changing hands)
            A ->
            B -> C, 40
            C -> D, 20
            D -> E, 50
            E ->
            F -> (E, 10), (D, 10), (C, 30), (B, 10)
            G -> (B, 30), (D, 10)

        A net owes 0 to group
        B net (40 - 30 - 10) = 0
        C net (-20 - 30) = -50
        D net (50 - 10 - 10) = + 10
        E net (0 - 10 - 50) = -60
        F net (10 + 10 + 30 + 10) = +60
        G net = (30 + 10) = 40


        """
        Flow.simplify_debt(self.messy).to_dot()

    def test_net_debts(self):
        """Checks that everyone is paid enough"""
        b, c, d, e, f, g = self.messy.nodes()

        # get initial weights in of everyone, compare to calculated values in weighted digraph
        di_debt = self.messy_as_digraph.net_debts()
        expected_debt = {b: 0, c: -50, d: 10, e: -60, f: 60, g: 40}

        # check for flow graph;

        edge: FlowEdge
        # send edge capacity down each edge
        for node, adj_list in self.messy.graph.items():
            for edge in adj_list:
                self.messy.push_flow([node, edge.node], edge.capacity)
        print(self.messy.to_dot())
        flow_debt = self.messy.net_debts()

        # for debt, label in zip([flow_debt], ['flow']):
        for debt, label in zip([di_debt, flow_debt], ["di", "flow"]):
            with self.subTest(label):
                self.assertEqual(expected_debt, debt)

        print(expected_debt, flow_debt, sep="\n")
