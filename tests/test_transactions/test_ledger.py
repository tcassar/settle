# coding=utf-8
import os
import unittest

import src.simplify.flow_graph
import src.simplify.graph_objects
from src.transactions.ledger import *
from src.crypto import keys
from src.transactions.transaction import VerificationError


def setUpModule():
    print(os.getcwd())
    os.chdir("/home/tcassar/projects/settle")


def key_path(usr: str, keytype="private") -> str:
    assert usr == "d" or usr == "m" or usr == "t"
    return f"./src/crypto/sample_keys/{usr}_{keytype}-key.pe{'m' if keytype == 'private' else ''}"


class TestLedger(unittest.TestCase):
    def setUp(self) -> None:
        self.valid: Ledger
        self.missing_key: Ledger
        self.invalid: Ledger

        # load in raw copies of d, m, t test keys
        ldr = keys.RSAKeyLoader()
        self.d_m_t_keys: dict[int, keys.RSAPrivateKey] = {}
        pubs: list[keys.RSAPublicKey] = []

        for person, id in zip(["d", "m", "t"], [4, 13, 20]):
            ldr.load(key_path(person))
            ldr.parse()
            self.d_m_t_keys[id] = keys.RSAPrivateKey(ldr)
            pubs.append(keys.RSAPublicKey(ldr))

        self.d_pub, self.m_pub, self.t_pub = pubs
        self.d_priv, self.m_priv, self.t_priv = self.d_m_t_keys.values()

        self.valid, self.missing_key, self.invalid = LedgerLoader.load_from_csv(
            "./tests/test_transactions/database.csv"
        )

    def test_add(self):

        with self.subTest("Add"):
            ledger = Ledger()
            self.assertFalse(not not ledger)
            ledger.append(Transaction(0, 0, 0, self.d_priv, self.m_priv))
            self.assertTrue(not not ledger)

        with self.subTest("Catch non transaction"), self.assertRaises(LedgerBuildError):
            ledger.append(6)  # type: ignore

    def test_load_from_csv(self):
        ledger_list = LedgerLoader.load_from_csv(
            "./tests/test_transactions/database.csv"
        )
        self.assertEqual(len(ledger_list), 3)

    def test_verify_transactions(self):
        """
        Make three ledgers:
            1) Valid transactions
            2) An unsigned transaction
            3) An invalid signature

        Check that first one goes through no issues, and that other two are caught
        """

        with self.subTest("unsigned"), self.assertRaises(VerificationError):
            self.valid._verify_transactions()

        # sign transactions in ledger; not normal procedure so contrived
        self.sign()

        with self.subTest("signed"):
            self.valid._verify_transactions()

        with self.subTest("missing key"), self.assertRaises(VerificationError):
            self.missing_key._verify_transactions()

        with self.subTest("invalid key"), self.assertRaises(VerificationError):
            self.invalid._verify_transactions()

    def test_as_flow(self):
        # sign ledger
        self.sign()

        Vertex = src.simplify.graph_objects.Vertex

        exp = src.simplify.flow_graph.FlowGraph(
            [Vertex(ID=4), Vertex(ID=13), Vertex(ID=20)]
        )
        d, m, t = exp.nodes()
        exp.add_edge(d, (m, 10), (t, 5))
        exp.add_edge(t, (m, 5))

        as_flow = self.valid._as_flow()

        with self.subTest("nodes"):
            self.assertEqual(exp.nodes(), self.valid.nodes)

        with self.subTest("to flow graph"):
            self.assertEqual(exp, as_flow)

    def sign(self):
        for trn in self.valid.ledger:
            trn.sign(self.d_m_t_keys[trn.src], origin="src")
            trn.sign(self.d_m_t_keys[trn.dest], origin="dest")
            print("verifying...")
            trn.verify()
            print("verified")

    def test_flow_to_transactions(self):
        self.maxDiff = None
        self.sign()
        as_flow = self.valid._as_flow()

        # remove sigs, ID, for comparison
        trn: Transaction
        for trn in self.valid.ledger:
            trn.ID = 0
            trn.signatures = {}

        with self.subTest("to transactions"):
            self.valid.ledger.sort(key=lambda trn: trn.amount)
            calc: list[Transaction] = self.valid._flow_to_transactions(as_flow)
            calc.sort(key=lambda trn: trn.amount)

            self.assertEqual(calc, self.valid.ledger)

    def test_simplify_ledger(self):
        self.sign()
        self.valid.simplify_ledger()

        trn = Transaction(4, 13, 15, self.d_pub, self.m_pub)

        self.assertEqual(self.valid.ledger, [trn])
