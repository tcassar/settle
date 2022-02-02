# coding=utf-8

"""
Testing sign / verify through RSA working as expected
"""
from transactions.transaction import Signable
from crypto import keys, rsa

import os
from unittest import TestCase


class TestTransaction(Signable):

    def __init__(self, msg: str):
        self.msg = msg
        self.signature: None | bytes = None

    def add_sig(self, sig: bytes):
        self.signature = sig

    def __str__(self):
        return self.msg


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
        private = keys.RSAPrivateKey(ldr)

        self.notary = rsa.Notary(private)
        self.tamper = TestTransaction('leng1')

        self.notary.sign_object(self.tamper)

    def test_sign_auth(self):
        # set up signable object

        test = TestTransaction('hello, world')

        notary = self.notary

        try:
            notary.sign_object(test)
        except rsa.SigningError:
            # leave signing error as it means there is problem in verification
            ...

        with self.subTest('Add signature'):
            self.assertIsNotNone(test.signature)

        with self.subTest('Verification'):
            notary.verify_object(test)

    def test_msg_tamper(self):
        tamper = self.tamper
        tamper.msg = 'dead1'

        with self.assertRaises(rsa.SigningError):
            self.notary.verify_object(tamper)

    def test_sig_tamper(self):
        tamper = self.tamper
        tamper.signature += b'1'

        with self.assertRaises(rsa.SigningError):
            self.notary.verify_object(tamper)

    def test_wrong_key(self):
        wrong_n = 18231757778644991469507401312789582877781534014553965177581396676839959606175435801863838402990543275146484795023094572359197711310781090953820140937277705965632717515037076770022347828011108355089986627552004992672393070894206395808799578541958959170028022893852482465561598422911676915676055536547944924762986113332647139161230437188417638711946503785852868377920318712400478389475428428734605979964295175769770577131851073719154592761435314474170377778421705523540586767451848335720653517574751974280104019370340042130060191775515076154552292298216482558770554460450166800518335449509480326048630771206402314778989
        wrong_e = 65537

        wrong_key = keys.TestPubKey(wrong_n, wrong_e)
        wrong_notary = rsa.RestictedNotary(wrong_key)

        with self.assertRaises(rsa.SigningError):
            wrong_notary.verify_object(self.tamper)




