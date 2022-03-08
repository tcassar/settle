# coding=utf-8
import os
import unittest
from src.transactions.transaction import *


class TestTransaction(unittest.TestCase):

    def test_hash(self):
        trn = Transaction(0, 0, 0)
        trn.time = 0
        self.assertEqual(trn.hash(), b'\xb9y\x8f\xe6\xdeo\x08\xd4\x1f\xdd\x01\xa3\xb4\xc5\x1d\x98\xd4\xac\x1bJ\x02\xd3\xa0\x01!\xf3\x99\xdf\xd5\\\x85v')
        trn.time = 1
        self.assertNotEqual(trn.hash(), b'\xb9y\x8f\xe6\xdeo\x08\xd4\x1f\xdd\x01\xa3\xb4\xc5\x1d\x98\xd4\xac\x1bJ\x02\xd3\xa0\x01!\xf3\x99\xdf\xd5\\\x85v')

    def test_sign(self):
        """Working on assumption that rsa.Notary is working; tested in settle/tests/test_crypto"""
        trn = Transaction(0, 0, 0)
        trn.time = 0  # type: ignore  # for a test case, not the norm

        # load keys
        os.chdir("/home/tcassar/projects/settle/src")
        ldr = keys.RSAKeyLoader()
        ldr.load("./crypto/sample_keys/private-key.pem")
        ldr.parse()

        key = keys.RSAPrivateKey(ldr)

        trn.sign(key, origin="src")

        with self.subTest("catch invalid origin"), self.assertRaises(ValueError):
            trn.sign(key, origin="no")

        with self.subTest("sig_overwrite"), self.assertRaises(TransactionError):
            trn.sign(key, origin="src")

        with self.subTest("Right sig"):
            self.assertEqual(b'\xc1~\xcbu\xecX\x01E*\xf2;O\xe3\xf3\x08x\xee\x84\xfc\xe1\xca\x8b\xa2\xedj\xec\x9b\xfd\xe5$7\x88n\xb7\x86\xfc~\x98\x91\x80Z\xcd\x1e\xf5}\xc2<JS\xefY\xe5UW\xfc\x0e\xd2\xbe\xc9\xea\xfbzm\xf2\xa7\x08\x8d\x05\x16\xe4@\xf40\x03I\xca\xbc.\x95\xbb\xd3\n\xfd9\xb0Wk\xf4\x03\x96\xdbF\xcd\xa0E\xd1\xac\xa6(\xb9\x92\xdb\x841\xe0U"\xe4\x7f\xeb U\xc9Z\xe5\xf6\x19\xc1Wn\x17&\x17\x84Dt\xb6z\xc0\x02\x85`\xf3\xd3\xd5\x98t7\xcd_\xfc\xa7\\\xa7t\xe8\xb1\xafl\x05\xb3\x07a\xd0jr\xc4}\xd8\xb58\xf4o\x9f\x02\xa2\xe6?3B\xf6\xe1\xe6\xb2\x02d\xfd\xd5\x83\xcf\xcc\xb6\x06m\xc2p\xd7\x00@\x93H\xc6]\x0c\x98\x1e\xdf\xda\x00\x86\xd7\xec\xc7\x10\x025eiry\xd6\x80\xfe\xe2+\xb8\x1dn\noB\xc0\xa8a\xc8t\xbfg\xbb\xca(Aj\xa5\xeb\x94\x0c-\xacr\'\xfe\n^Z\x13\xa0\'\xaa\x96{\xf8x\xce\xd6\x90', trn.signatures[trn.src])


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
