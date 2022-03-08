# coding=utf-8
import os
import unittest

from src.transactions.ledger import *


def setUpModule():
    print(os.getcwd())


def key_path(usr: str) -> str:
    assert usr == ('d' or 'm' or 't')
    return f'../src/crypto/sample_keys/{usr}_private-key.pem'


class TestLedger(unittest.TestCase):
    def test_add(self):

        with self.subTest("Add"):
            ledger = Ledger()
            self.assertFalse(not not ledger)
            ledger.append(Transaction(0, 0, 0))
            self.assertTrue(not not ledger)

        with self.subTest("Catch non transaction"), self.assertRaises(LedgerBuildError):
            ledger.append(6)  # type: ignore

    def test_load_from_csv(self):
        trn_list = str(LedgerLoader.load_from_csv('./test_transactions/database.csv'))
        exp = "[[Transaction(src='d', dest='t', amount=5, ID=0, msg='', signatures={})], [Transaction(src='d', dest='m', amount=10, ID=1, msg='', signatures={})], [Transaction(src='t', dest='m', amount=5, ID=2, msg='', signatures={})], [Transaction(src='d', dest='t', amount=5, ID=3, msg='', signatures={})], [Transaction(src='d', dest='m', amount=10, ID=4, msg='', signatures={}), Transaction(src='t', dest='m', amount=5, ID=5, msg='', signatures={}), Transaction(src='d', dest='t', amount=5, ID=6, msg='', signatures={}), Transaction(src='d', dest='m', amount=10, ID=7, msg='', signatures={}), Transaction(src='t', dest='m', amount=5, ID=8, msg='', signatures={})]]"
        self.assertEqual(exp, trn_list)


    def test_verify_transactions(self):
        """
        Make three ledgers:
            1) Valid transactions
            2) An unsigned transaction
            3) An invalid signature

        Check that first one goes through no issues, and that other two are caught
        """
