# coding=utf-8

"""
Testing sign / verify through RSA working as expected
"""
from crypto import keys, hashes
from crypto.rsa import RSA, DecryptionError

import os
from unittest import TestCase


def setUpModule():
    os.chdir("/home/tcassar/projects/settle/")


class TestRSA(TestCase):
    """Just tests RSA parts"""

    def setUp(self) -> None:
        # load keys
        ldr = keys.RSAKeyLoader()
        ldr.load("./crypto/sample_keys/private-key.pem")
        ldr.parse()

        # build public and private
        self.private = keys.RSAKey(ldr)
        self.public = keys.RSAPublicKey(ldr)

    def test_encryption(self):
        """Checks to see if process is reversible, and encrypted is different to how it started"""
        message = "hello, world"
        m_bytes = bytes(message, encoding="utf8")
        encrypted = RSA.encrypt(m_bytes, self.public)
        # TODO: actually fix byte overflow affair
        decrypted = RSA.bytes_to_str(RSA.naive_decrypt(encrypted, self.private))

        with self.subTest("Catch Public Key"):
            with self.assertRaises(DecryptionError):
                _ = RSA.naive_decrypt(encrypted, self.public)

        with self.subTest("encrypted"):
            self.assertNotEqual(m_bytes, encrypted)

        with self.subTest("Successful decryption"):
            self.assertEqual(message, decrypted)
