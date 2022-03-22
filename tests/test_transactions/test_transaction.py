# coding=utf-8
import os
import unittest

from src.transactions.transaction import *


class TestTransaction(unittest.TestCase):
    def setUp(self) -> None:
        # load keys
        os.chdir("/home/tcassar/projects/settle/src")
        ldr = keys.RSAKeyLoader()
        ldr.load("./crypto/sample_keys/d_private-key.pem")
        ldr.parse()

        self.key = keys.RSAPrivateKey(ldr)
        self.pub_key = keys.RSAPublicKey(ldr)

        self.trn = Transaction(0, 0, 0, self.pub_key, self.pub_key)
        self.trn.time = 0  # type: ignore

    def test_hash(self):
        """Tests that calling .hash() on a Transaction displays expected behaviour"""
        self.assertEqual(
            self.trn.hash(),
            b"\xb9y\x8f\xe6\xdeo\x08\xd4\x1f\xdd\x01\xa3\xb4\xc5\x1d\x98\xd4\xac\x1bJ\x02\xd3\xa0\x01!\xf3\x99\xdf\xd5\\\x85v",
        )
        self.trn.time = 1
        self.assertNotEqual(
            self.trn.hash(),
            b"\xb9y\x8f\xe6\xdeo\x08\xd4\x1f\xdd\x01\xa3\xb4\xc5\x1d\x98\xd4\xac\x1bJ\x02\xd3\xa0\x01!\xf3\x99\xdf\xd5\\\x85v",
        )

    def test_sign(self):
        """
        Checks that signing a Transaction displays expected behaviour
        Working on assumption that rsa.Notary is working; tested in settle/tests/test_crypto"""

        self.trn.sign(self.key, origin="src")

        with (self.subTest("catch invalid origin"), self.assertRaises(ValueError)):
            self.trn.sign(self.key, origin="no")

        with self.subTest("invalid key types"), self.assertRaises(TransactionError):
            self.trn.sign(12, origin="src")
            self.trn.sign(self.pub_key, origin="dest")

        with self.subTest("sig_overwrite"), self.assertRaises(TransactionError):
            self.trn.sign(self.key, origin="src")

        with self.subTest("Right sig"):
            self.assertEqual(
                b"\xc1~\xcbu\xecX\x01E*\xf2;O\xe3\xf3\x08x\xee\x84\xfc\xe1\xca\x8b\xa2\xedj\xec\x9b\xfd\xe5$7\x88n\xb7\x86\xfc~\x98\x91\x80Z\xcd\x1e\xf5}\xc2<JS\xefY\xe5UW\xfc\x0e\xd2\xbe\xc9\xea\xfbzm\xf2\xa7\x08\x8d\x05\x16\xe4@\xf40\x03I\xca\xbc.\x95\xbb\xd3\n\xfd9\xb0Wk\xf4\x03\x96\xdbF\xcd\xa0E\xd1\xac\xa6(\xb9\x92\xdb\x841\xe0U\"\xe4\x7f\xeb U\xc9Z\xe5\xf6\x19\xc1Wn\x17&\x17\x84Dt\xb6z\xc0\x02\x85`\xf3\xd3\xd5\x98t7\xcd_\xfc\xa7\\\xa7t\xe8\xb1\xafl\x05\xb3\x07a\xd0jr\xc4}\xd8\xb58\xf4o\x9f\x02\xa2\xe6?3B\xf6\xe1\xe6\xb2\x02d\xfd\xd5\x83\xcf\xcc\xb6\x06m\xc2p\xd7\x00@\x93H\xc6]\x0c\x98\x1e\xdf\xda\x00\x86\xd7\xec\xc7\x10\x025eiry\xd6\x80\xfe\xe2+\xb8\x1dn\noB\xc0\xa8a\xc8t\xbfg\xbb\xca(Aj\xa5\xeb\x94\x0c-\xacr'\xfe\n^Z\x13\xa0'\xaa\x96{\xf8x\xce\xd6\x90",
                self.trn.signatures[self.trn.src],
            )

    def test_verify(self):
        """Checks that we are able to verify transactions"""
        # check that we are complained at if no valid keys are passed in
        with self.subTest("catch invalid keys"), self.assertRaises(VerificationError):
            self.trn.verify()
            self.trn.verify()  # wrong type  # type: ignore

        # check works with priv and public keys

        with self.subTest("good verif"):
            self.trn.sign(self.key, origin="src")
            self.trn.verify()

        with self.subTest("priv/pub keys"):
            self.trn.verify()
            self.trn.verify()

        with self.subTest("verify src, dest"):
            self.trn.verify()
            self.trn.verify()

        with self.subTest("verify >1 param"):
            self.trn.verify()

        with self.subTest("bad key"), self.assertRaises(VerificationError):
            # edit pub key, thus should fail
            self.pub_key.lookup["n"] = 3
            self.trn.verify()
