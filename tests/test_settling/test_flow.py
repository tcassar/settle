# coding=utf-8
from unittest import TestCase

from src.simplify.flow_algorithms import NoOptimisations, MaxFlow, Simplify
from src.simplify.flow_graph import *
from src.simplify.graph_objects import Vertex


class TestFlowEdge(TestCase):
    """Tests for FlowEdge"""

    def setUp(self) -> None:
        self.edges = [FlowEdge(Vertex(0), Vertex(1), 5 * n) for n in range(2)]
        self.edges[0].flow = -3  # => unused capacity should be three

    def test_unused_capacity(self):
        """builds two edges, residual and non-residual
        non-residual has capacity 5"""

        for edge, cap in zip(self.edges, [3, 5]):
            with self.subTest(edge):
                self.assertEqual(edge.unused_capacity(), cap)

    def test_push_flow(self):
        """Checks that we update flow by required amount"""
        # push three units of capacity through each edge
        for edge, exp in zip(self.edges, [0, 2]):
            with self.subTest(edge):
                edge.push_flow(3)
                self.assertEqual(exp, edge.unused_capacity())

        # try to push excess amount of flow down an edge
        with self.subTest("exceed capacity"), self.assertRaises(FlowEdgeError):
            self.edges[1].push_flow(3)

    def test_adjust_edge(self):
        """Tests that the adjust_edges function works as expected
        i.e when adjust is called, edges in the graph morph to edges with a flow equal to their unused capacity
        and all edges of weight 0 are deleted"""
        (
            res,
            fwd,
        ) = self.edges
        fwd.push_flow(3)
        res.push_flow(-3)

        new_fwd = FlowEdge(Vertex(0), Vertex(1), 2)
        new_res = FlowEdge(Vertex(0), Vertex(1), 0)

        fwd.adjust_edge()
        res.adjust_edge()

        self.assertEqual(new_fwd, fwd)
        self.assertEqual(new_res, res)

        # catch EdgeCapacityZero
        with self.assertRaises(EdgeCapacityZero):
            fwd.push_flow(2)
            fwd.adjust_edge()


class TestFlowGraph(TestCase):
    def setUp(self) -> None:
        # make some nodes for a graph
        self.nodes = [Vertex(n, label=chr(n + 97)) for n in range(5)]
        self.graph = FlowGraph(self.nodes)

    def test_is_edge(self):
        a, b, c, d, e = self.nodes

        with self.subTest("no edge"):
            self.assertFalse(self.graph.is_edge(a, b))

        with self.subTest("edge"):
            self.graph.add_edge(a, (b, 4))
            self.assertTrue(self.graph.is_edge(a, b))

    def test_get_edge(self):
        a, b, c, d, e = self.graph.nodes()
        self.graph.add_edge(a, (b, 5))
        self.assertEqual(FlowEdge(a, b, 5), self.graph.get_edge(a, b))

    def test_add_edge(self):
        a, b, c, d, e = self.nodes
        # check there aren't edges
        with self.subTest("negative test"):
            self.assertFalse(self.graph.is_edge(a, b))
            self.assertFalse(self.graph.is_edge(b, a, residual=True))
        self.graph.to_dot()
        self.graph.add_edge(a, (b, 5))
        self.graph.to_dot()
        with self.subTest("added"):
            self.assertTrue(self.graph.is_edge(a, b))
            self.assertTrue(self.graph.is_edge(b, a, residual=True))
            self.assertFalse(self.graph.is_edge(b, a))

        with self.subTest("Net debt (adding)"):
            self.assertEqual(
                {
                    Vertex(ID=0, label="a"): 5,
                    Vertex(ID=1, label="b"): -5,
                    Vertex(ID=2, label="c"): 0,
                    Vertex(ID=3, label="d"): 0,
                    Vertex(ID=4, label="e"): 0,
                },
                self.graph.net_debt,
            )

        with self.subTest("Net debt (removing)"):
            self.graph.pop_edge(a, b, update_debt=True)
            self.assertEqual(
                {
                    Vertex(ID=0, label="a"): 0,
                    Vertex(ID=1, label="b"): 0,
                    Vertex(ID=2, label="c"): 0,
                    Vertex(ID=3, label="d"): 0,
                    Vertex(ID=4, label="e"): 0,
                },
                self.graph.net_debt,
            )

    def test_pop_edge(self):
        a, b, c, d, e = self.nodes

        self.graph.add_edge(a, (b, 5))

        with self.subTest("negative"):
            self.assertTrue(self.graph.is_edge(a, b))
            self.assertTrue(self.graph.is_edge(b, a, residual=True))

        self.graph.pop_edge(a, b)

        with self.subTest("removed edge"):
            self.assertFalse(self.graph.is_edge(a, b))
        with self.subTest("removed residual"):
            self.assertFalse(self.graph.is_edge(b, a, residual=True))

    def test_flow_neighbours(self):
        """Checks we get edges that have unused capacity, including residual
        These edges count as valid paths to neighbouring nodes in Edmonds-Karp"""
        graph = self.graph
        a, b, c, d, *_ = graph.nodes()
        graph.add_edge(a, (b, 10))
        graph.add_edge(b, (c, 2))
        graph.add_edge(c, (d, 10))
        graph.add_edge(d, (a, 10))

        graph.to_dot()

        MaxFlow.augment_flow(graph, [a, b, c, d], 2)
        c_flow_neighbours = graph.flow_neighbours(c)
        self.assertEqual([d, b], GenericDigraph.nodes_from_edges(c_flow_neighbours))

    def test_bool(self):
        """Tests that dunder bool method returns true when there are edges in the graph"""
        # empty
        print(self.graph.graph)
        self.assertFalse(bool(self.graph))

        # with an edge
        a, b, c, d, e = self.nodes
        self.graph.add_edge(a, (b, 10))

    def test_add_existing(self):
        """Tests that adding an existing edge will add capacity onto the existing edge,
        as opposed to adding a new distinct edge from src -> dest"""
        a, b, c, d, e = self.graph.nodes()
        self.graph.add_edge(a, (b, 5))
        self.graph.add_edge(a, (b, 5))
        print(self.graph)
        self.assertEqual(self.graph.get_edge(a, b).capacity, 10)

    def test_pop_existing(self):
        """Tests that if an edge A -> B of weight [5] exists, adding B -> A [5] will remove
        any edges between A and B, as there is net 0 between the two"""
        a, b, c, d, e = self.graph.nodes()
        self.graph.add_edge(a, (b, 5))
        self.graph.add_edge(b, (a, 5))

        self.assertFalse(self.graph.is_edge(a, b))

    def test_add_edge_reverses_new_edge(self):
        """Checks that if there exists an edge A -> B of weight [5] exists, adding B -> A [10] will
        reverse the direction of the edge such that now an edge B -> A [5] exists"""
        a, b, c, d, e = self.graph.nodes()
        self.graph.add_edge(a, (b, 5))
        self.graph.add_edge(b, (a, 10))

        self.assertFalse(self.graph.is_edge(a, b))
        self.assertEqual(self.graph.get_edge(b, a).capacity, 5)


class TestMaxFlow(TestCase):
    def setUp(self) -> None:
        graph = FlowGraph([Vertex(n, label=chr(n + 97)) for n in range(4)])
        a, b, c, d, *_ = graph.nodes()
        graph.add_edge(a, (b, 10))
        graph.add_edge(b, (c, 2))
        graph.add_edge(c, (d, 10))
        graph.add_edge(d, (a, 10))

        self.graph = graph

    def test_bottleneck(self):
        """Checks we get the correct bottleneck value on a path"""
        # build a chain with an obvious bottleneck on normal graphs
        graph = self.graph
        a, b, c, d, *_ = graph.nodes()

        aug_path = [a, b, c, d]

        graph.to_dot()

        self.assertEqual(2, MaxFlow.bottleneck(graph, aug_path))

    def test_nodes_to_path(self):
        """Checks that we can build a path of edges from nodes"""
        a, b, c, d, *_ = self.graph.nodes()
        edges = MaxFlow.nodes_to_path(self.graph, [a, b, c, d])

        self.assertEqual(
            edges, [FlowEdge(a, b, 10), FlowEdge(b, c, 2), FlowEdge(c, d, 10)]
        )

    def test_augmenting_path(self):
        """Tests that we find valid augmenting paths"""
        a, b, c, d, *_ = self.graph.nodes()
        MaxFlow.augmenting_path(self.graph, a, d)

    def test_augment_flow(self):
        """Checks that augmenting flow works exactly as described in Analysis"""
        a, b, c, d, *_ = self.graph.nodes()

        MaxFlow.augment_flow(self.graph, [a, b, c, d], 2)
        self.graph.to_dot()

        # check that the edges and residual edges all now have flow 2
        node_path = [a, b, c, d]
        flow = 2
        for _ in range(2):
            # one for normal one for residual
            for src, dest in zip(node_path, node_path[1:]):
                with self.subTest(f"{src} -> {dest}"):
                    self.assertEqual(flow, self.graph.get_edge(src, dest).flow)
            # change path to be residual, flow changes accordingly
            node_path.reverse()
            flow *= -1

    def test_edmonds_karp(self):
        """Integration test for edmonds-karp, ensures that max flow is correct"""
        # build slightly more involved graph
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

        tg.to_dot()

        max_flow = MaxFlow.edmonds_karp(tg, s, t)
        self.assertEqual(max_flow, 20)

    def test_old_edmonds(self):
        """Tests a more complex graph for correct maxflow"""
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

        a, b, c, d, e, f = self.vertices

        expected = 20
        calculated = MaxFlow.edmonds_karp(self.flow_graph, a, f)

        self.assertEqual(expected, calculated)


class TestSimplify(TestCase):  # type: ignore
    def setUp(self) -> None:
        self.graph = FlowGraph([Vertex(0, "d"), Vertex(1, "m"), Vertex(2, "t")])
        d, m, t = self.graph.nodes()
        self.graph.add_edge(d, (m, 5), (t, 10))
        self.graph.add_edge(m, (t, 5))

    def test_simplify_debt(self):
        """Uses graph from analysis to test that the debt simplifying algorithm simplifies debt, does not create or
        destroy debt"""

        print(self.graph.net_debt)

        people = ["dad", "tom", "maia"]
        debt = FlowGraph([Vertex(ID, person) for ID, person in enumerate(people)])

        d, t, m = debt.nodes()

        debt.add_edge(d, (t, 10), (m, 5))
        debt.add_edge(m, (t, 5))

        debt.to_dot()

        clean = Simplify.simplify_debt(debt)

        clean.to_dot(n=1)
        self.assertEqual(debt.net_debt, clean.net_debt)

    def test_adjust_edges(self):

        """Checks that edges are adjusted accordingly, generate graphs before and after"""

        # saturate d -> m -> t
        self.graph.to_dot(n=0)
        d, m, t = self.graph.nodes()
        MaxFlow.augment_flow(self.graph, [d, m, t], 5)
        self.graph.to_dot(n=1)
        self.graph.adjust_edges()
        self.graph.to_dot(n=4)

        # graph should have no edges in or out of m
        # t should have a res edge to d, 0/0
        # d should have a fwd to t, 0/10

        self.assertFalse(self.graph[m])
        self.assertEqual(self.graph[d], [FlowEdge(d, t, 10)])
        self.assertEqual(self.graph[t], [FlowEdge(t, d, 0)])

    def test_mithun_simplify(self):

        """Checks more complex example, ensures that graph is settled and that no debt is created / destroyed"""

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

        messy.to_dot()

        clean = Simplify.simplify_debt(messy)
        clean.to_dot(n=1)

        self.assertEqual(messy.net_debt, clean.net_debt)

    def test_simplest_graph(self):
        """Shouldn't change"""
        people = ["dad", "tom", "maia"]
        debt = FlowGraph([Vertex(ID, person) for ID, person in enumerate(people)])
        d, t, m = debt.nodes()
        debt.add_edge(d, (t, 5))
        debt.add_edge(t, (m, 10))

        debt.to_dot()

        with self.assertRaises(NoOptimisations):
            clean = Simplify.simplify_debt(debt)
            clean.to_dot(n=1)
