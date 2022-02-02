# coding=utf-8

"""
Testing sign / verify through RSA working as expected
"""
from transactions.transaction import Signable
from crypto import keys, rsa

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
        self.private = keys.RSAPrivateKey(ldr)
        self.public = keys.RSAPublicKey(ldr)

    def test_encryption(self):
        """Checks to see if process is reversible, and encrypted is different to how it started"""
        message = " | maia"
        m_bytes = bytes(message, encoding="utf8")
        encrypted = rsa.RSA.encrypt(m_bytes, self.public)
        # TODO: actually fix byte overflow affair
        decrypted = rsa.RSA.bytes_to_str(rsa.RSA.naive_decrypt(encrypted, self.private))

        with self.subTest("Catch Public Key"):
            with self.assertRaises(rsa.DecryptionError):
                _ = rsa.RSA.naive_decrypt(encrypted, self.public)

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


class TestNotary(TestCase):
    """Test interface to sign signable objects"""

    def setUp(self) -> None:
        # load keys
        ldr = keys.RSAKeyLoader()
        ldr.load("./crypto/sample_keys/private-key.pem")
        ldr.parse()

        # build public and private
        self.private = keys.RSAPrivateKey(ldr)
        self.public = keys.RSAPublicKey(ldr)

    def test_sign_auth(self):
        # set up signable object

        class TestTransaction(Signable):

            def __init__(self, msg: str):
                self.msg = msg
                self.signature: None | bytes = None

            def add_sig(self, sig: bytes):
                self.signature = sig

            def __str__(self):
                return self.msg

        test = TestTransaction('hello, world')

        notary = rsa.Notary(self.private)

        try:
            notary.sign_object(test)
        except rsa.SigningError:
            # leave signing error as it means there is problem in verification
            ...

        with self.subTest('Add signature'):
            self.assertIsNotNone(test.signature)
            print(test.signature)

        with self.subTest('Verification'):
            self.assertTrue(notary.verify_object(test))
