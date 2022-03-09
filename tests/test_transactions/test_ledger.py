# coding=utf-8
import os
import unittest

from src.transactions.ledger import *
from src.crypto import keys


def setUpModule():
    print(os.getcwd())


def key_path(usr: str) -> str:
    assert usr == 'd' or usr == 'm' or usr == 't'
    return f'../src/crypto/sample_keys/{usr}_private-key.pem'


class TestLedger(unittest.TestCase):

    def setUp(self) -> None:
        self.valid: Ledger
        self.missing_key: Ledger
        self.invalid: Ledger

        # load in raw copies of d, m, t test keys
        ldr = keys.RSAKeyLoader()
        d_m_t_keys: list[keys.RSAPublicKey] = []

        for person in ['d', 'm', 't']:
            ldr.load(key_path(person))
            ldr.parse()
            d_m_t_keys.append(keys.RSAPublicKey(ldr))

        self.d_pub, self.m_pub, self.t_pub = d_m_t_keys

        self.valid, self.missing_key, self.invalid = LedgerLoader.load_from_csv('./test_transactions/database.csv')

    def test_add(self):

        with self.subTest("Add"):
            ledger = Ledger()
            self.assertFalse(not not ledger)
            ledger.append(Transaction(0, 0, 0, self.d_pub, self.m_pub))
            self.assertTrue(not not ledger)

        with self.subTest("Catch non transaction"), self.assertRaises(LedgerBuildError):
            ledger.append(6)  # type: ignore

    def test_load_from_csv(self):
        ledger_list = LedgerLoader.load_from_csv('./test_transactions/database.csv')
        self.assertEqual(len(ledger_list), 3)

    def test_verify_transactions(self):
        """
        Make three ledgers:
            1) Valid transactions
            2) An unsigned transaction
            3) An invalid signature

        Check that first one goes through no issues, and that other two are caught
        """

        with self.subTest('signed'):
            self.valid._verify_transactions()

        with self.subTest("missing key"), self.assertRaises(VerificationError):
            self.missing_key._verify_transactions()

        with self.subTest("invalid key"), self.assertRaises(VerificationError):
            self.invalid._verify_transactions()
