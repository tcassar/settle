# coding=utf-8
import unittest
from src.transactions.transaction import *


class TestLedger(unittest.TestCase):
    def test_add(self):

        with self.subTest("Add"):
            ledger = Ledger()
            self.assertFalse(not not ledger)
            ledger.append(Transaction(0, 0, 0))
            self.assertTrue(not not ledger)

        with self.subTest("Catch non transaction"), self.assertRaises(LedgerBuildError):
            ledger.append(6)  # type: ignore


if __name__ == "__main__":
    unittest.main()
