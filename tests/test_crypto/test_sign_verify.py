# coding=utf-8

"""
Testing sign / verify through RSA working as expected
"""
import os
import pathlib
from unittest import TestCase

from src.crypto import keys
from src.crypto import rsa
from src.transactions.transaction import Signable


def setUpModule():
    os.chdir(pathlib.Path(__file__).parent.parent.parent / "src")


class TestRSA(TestCase):
    """Just tests RSA parts"""

    def setUp(self) -> None:
        # load keys
        ldr = keys.RSAKeyLoader()
        ldr.load("./crypto/sample_keys/d_private-key.pem")
        ldr.parse()

        # build public and private
        self.private = keys.RSAPrivateKey(ldr)
        self.public = keys.RSAPublicKey(ldr)

    def test_encryption(self):
        """Checks to see if process is reversible, and encrypted is different to how it started"""
        message = " | maia"
        m_bytes = bytes(message, encoding="utf8")
        encrypted = rsa.RSA.encrypt(m_bytes, self.public)
        decrypted = rsa.RSA.bytes_to_str(rsa.RSA.naive_decrypt(encrypted, self.private))

        with self.subTest("Catch Public Key"):
            with self.assertRaises(rsa.DecryptionError):
                _ = rsa.RSA.naive_decrypt(encrypted, self.public)  # type: ignore

        with self.subTest("encrypted"):
            self.assertNotEqual(m_bytes, encrypted)

        with self.subTest("Successful decryption"):
            self.assertEqual(message, decrypted)

    def test_RSA_sign(self):
        """Checks for consistent creating / verifying of a 'signature'"""

        message = " | maia"
        m_bytes = message.encode("utf8")
        sig: bytes = rsa.RSA.sign(m_bytes, self.private)
        de_sign: bytes = rsa.RSA.inv_sig(sig, self.public)

        self.assertEqual(m_bytes, de_sign)
