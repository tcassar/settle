# coding=utf-8
import unittest
from src.transactions.transaction import *
from src.crypto import *


class TestTransaction(unittest.TestCase):
    
    def test_sign(self):
        """Working on assumption that rsa.Notary is working; tested in settle/tests/test_crypto"""
        trn = Transaction(0, 0, 0)

        trn.sign(b'123', origin='src')

        with self.subTest('catch invalid origin'), self.assertRaises(ValueError):
            trn.sign(b'123', origin='no')

        with self.subTest('sig_overwrite'), self.assertRaises(TransactionError):
            trn.sign(b'123', origin='src')




class TestLedger(unittest.TestCase):
    def test_add(self):

        with self.subTest("Add"):
            ledger = Ledger()
            self.assertFalse(not not ledger)
            ledger.append(Transaction(0, 0, 0))
            self.assertTrue(not not ledger)

        with self.subTest("Catch non transaction"), self.assertRaises(LedgerBuildError):
            ledger.append(6)  # type: ignore

    def test_verify_transactions(self):
        """
        Make three ledgers:
            1) Valid transactions
            2) An unsigned transaction
            3) An invalid signature

        Check that first one goes through no issues, and that other two are caught
        """




